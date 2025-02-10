<script lang="ts">
	import { getJson, putWithParams } from '$lib/api/base-api'
	import LoadingScreen from '$lib/components/loading/LoadingScreen.svelte'
	import { onMount, tick } from 'svelte'
	import { error, success } from '$lib/components/toast/toast-store.svelte'
	import ModeSelection from '$lib/components/mode-selection/ModeSelection.svelte'
	import EditableNumber from '$lib/components/input/EditableNumber.svelte'
	import Chart, { type ChartItem } from 'chart.js/auto'
	import dayjs from 'dayjs'
	import 'chartjs-adapter-dayjs-4/dist/chartjs-adapter-dayjs-4.esm'
	type Mode = 'off' | 'auto' | 'manual' | 'boil' | 'tuning'

	type Status = {
		mode: Mode
		pump: boolean
		temperature: number
		setpoint: number
		dutyCycle: number
		chartX: number[]
		chartTemperatureY: number[]
		chartSetpointY: (number | null)[]
		chartDutyCycleY: number[]
		boilAchieved: boolean
		autotunePeakCount?: number
	}

	let status: Status | undefined = $state()
	let chartObject: Chart

	const chartData = {
		labels: [] as number[],
		datasets: [
			{
				label: 'Temperature',
				data: [] as { x: number; y: number }[],
				yAxisID: 'y',
				spanGaps: true,
			},
			{
				label: 'Setpoint',
				data: [] as { x: number; y: number }[],
				yAxisID: 'y',
				spanGaps: false,
			},
			{
				label: 'Heater power',
				data: [] as { x: number; y: number }[],
				yAxisID: 'y1',
				spanGaps: true,
			},
		],
	}

	function setupChart() {
		chartObject = new Chart(document.getElementById('chart') as ChartItem, {
			type: 'line',
			data: chartData,
			options: {
				clip: false,
				normalized: true,
				elements: {
					point: {
						radius: 0,
					},
				},
				events: [],
				animation: false,
				scales: {
					x: {
						type: 'time',
						time: {
							displayFormats: {
								millisecond: 'HH:mm:ss',
								second: 'HH:mm:ss',
								minute: 'HH:mm',
							},
						},
						ticks: {
							source: 'labels',
							minRotation: 0,
							maxRotation: 0,
							align: 'center',
						},
						grid: { display: false },
						border: { display: false },
					},
					y: {
						type: 'linear',
						display: true,
						position: 'left',
						grid: { display: false },
						border: { display: false },
						ticks: {
							callback: (value) => value + '°C',
						},
					},
					y1: {
						type: 'linear',
						display: true,
						position: 'right',
						min: 0,
						max: 100,
						grid: { display: false },
						border: { display: false },
						ticks: {
							callback: (value) => value + '%',
						},
					},
				},
			},
		})
	}

	function getSeries(data: (number | null)[], millis: number[]) {
		const out: { x: number; y: number }[] = []
		for (let i = 0; i < data.length; i++) {
			if (data[i] != null) {
				out.push({ x: millis[i], y: data[i] as number })
			}
		}
		return out
	}

	const update = () => {
		return getJson<Status>('/status')
			.then((result) => {
				status = result
				tick().then(() => {
					if (chartObject == null) {
						setupChart()
					}
					chartData.labels.splice(0, chartData.labels.length)
					chartData.labels.push(result.chartX[0])
					if (result.chartX.length > 1) {
						chartData.labels.push(
							Math.floor((result.chartX[0] + result.chartX[result.chartX.length - 1]) / 2),
						)
						chartData.labels.push(result.chartX[result.chartX.length - 1])
					}
					chartData.datasets[0].data.splice(0, chartData.datasets[0].data.length)
					chartData.datasets[0].data.push(...getSeries(result.chartTemperatureY, result.chartX))
					chartData.datasets[1].data.splice(0, chartData.datasets[1].data.length)
					chartData.datasets[1].data.push(...getSeries(result.chartSetpointY, result.chartX))
					chartData.datasets[2].data.splice(0, chartData.datasets[2].data.length)
					chartData.datasets[2].data.push(...getSeries(result.chartDutyCycleY, result.chartX))
					chartObject.update()
				})
			})
			.catch(() => {
				error('Error getting status update!')
			})
	}

	function setDutyCycle() {
		return status == null
			? Promise.resolve()
			: putWithParams('/duty-cycle', { dutyCycle: status.dutyCycle })
	}

	function setSetpoint() {
		return status == null
			? Promise.resolve()
			: putWithParams('/setpoint', { setpoint: status.setpoint })
	}

	function togglePump(): void {
		if (status == null) return
		const newPumpStatus = !status.pump
		putWithParams('/pump', { pump: newPumpStatus })
			.then(() => {
				if (status != null) status.pump = newPumpStatus
				success(`Turning ${newPumpStatus ? 'on' : 'off'} the pump.`)
				update()
			})
			.catch(() => {
				error('Error toggling pump!')
			})
	}

	function setMode(mode: Mode) {
		return putWithParams('/mode', { mode })
	}

	let updateInterval: number

	onMount(() => {
		update()
		updateInterval = setInterval(update, 1000)
		document.addEventListener('refreshData', update)
		return () => {
			clearInterval(updateInterval)
			document.removeEventListener('refreshData', update)
		}
	})
</script>

{#if status == null}
	<LoadingScreen />
	<!-- svelte-ignore a11y_no_static_element_interactions -->
{:else}
	<ModeSelection
		modes={['off', 'auto', 'manual', 'boil']}
		bind:active={status.mode}
		errorMessage="Error changing mode!"
		confirmationMessage={status.mode == 'tuning'
			? 'Are you sure you want to cancel PID tuning?'
			: undefined}
		updateFunction={setMode}
		afterUpdate={update}
	>
		<div class="inline-block">Mode:</div>
	</ModeSelection>
	<div class="h-50 w-2/6">{status.temperature}°C</div>
	<div class="h-50 w-2/6">{status.dutyCycle}%</div>
	<div class="h-50 w-3/6"><canvas id="chart"></canvas></div>
	<div class="h-50 w-5/6">
		{#if status.mode === 'auto'}
			<EditableNumber
				name="Setpoint"
				suffix="°C"
				nonZero
				min={0}
				bind:value={status.setpoint}
				updateFunction={setSetpoint}
				afterUpdate={update}
			/>
		{:else if status.mode === 'manual'}
			<EditableNumber
				name="Power"
				suffix="%"
				nonZero
				min={0}
				max={100}
				bind:value={status.dutyCycle}
				updateFunction={setDutyCycle}
				afterUpdate={update}
			/>
		{/if}
	</div>
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="h-50 w-2/6" onclick={togglePump}>Pump: {status.pump}</div>
{/if}
