<script lang="ts">
	import { getJson, putWithParams } from '$lib/api/base-api'
	import LoadingScreen from '$lib/components/loading/LoadingScreen.svelte'
	import { onMount, tick } from 'svelte'
	import { error, success } from '$lib/components/toast/toast-store.svelte'
	import EditableNumber from '$lib/components/input/EditableNumber.svelte'
	import Chart, { type ChartItem } from 'chart.js/auto'
	import 'chartjs-adapter-dayjs-4/dist/chartjs-adapter-dayjs-4.esm'
	import Grid from '$lib/components/grid/Grid.svelte'
	import GridElement from '$lib/components/grid/GridElement.svelte'
	import StatusIcon from '$lib/components/main/StatusIcon.svelte'
	type Mode = 'off' | 'auto' | 'manual' | 'boil' | 'tuning'

	type Status = {
		mode: Mode
		pump: boolean
		temperature?: number
		setpoint: number
		dutyCycle: number
		chartX: number[]
		chartTemperatureY: (number | null)[]
		chartSetpointY: (number | null)[]
		chartDutyCycleY: number[]
		boilAchieved: boolean
		autotunePeakCount?: number
	}

	let status: Status | undefined = $state()
	let chartObject: Chart

	let modeText = $derived.by(() => {
		if (status == null) {
			return 'Loading...'
		}
		switch (status.mode) {
			case 'off':
				return status.temperature == null ? 'Temperature sensor error, heater off' : 'Heater off'
			case 'auto':
				return 'Holding temperature'
			case 'manual':
				return 'Holding duty cycle'
			case 'boil':
				return status.boilAchieved ? 'Boiling' : 'Heating up to a boil'
			case 'tuning':
				return 'Tuning PID parameters'
		}
	})

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
				label: 'Duty cycle',
				data: [] as { x: number; y: number }[],
				yAxisID: 'y1',
				spanGaps: true,
			},
		],
	}

	function formatTemp(value: number) {
		return (Math.round(value * 100) / 100).toFixed(2) + '°C'
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
							callback: (value) => formatTemp(value as number),
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
				update()
			})
			.catch(() => {
				error('Error toggling pump!')
			})
	}

	function setMode(mode: Mode) {
		return putWithParams('/mode', { mode })
	}

	const cancelTuningMessage = 'Are you sure you want to cancel PID tuning?'

	function shouldCancelTuning() {
		return status?.mode !== 'tuning' || confirm(cancelTuningMessage)
	}

	function changeMode(
		mode: Mode,
		options?: { confirmationMessage?: string; successMessage?: string; errorMessage?: string },
	) {
		if (
			options?.confirmationMessage != null
				? confirm(options.confirmationMessage)
				: shouldCancelTuning()
		) {
			setMode(mode)
				.then(() => {
					if (options?.successMessage) {
						success(options.successMessage)
					}
				})
				.catch(() => {
					error(options?.errorMessage ?? 'Error changing mode!')
				})
				.finally(update)
		}
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
	<Grid rows={4} cols={7}>
		<GridElement col={1} row={1} click={() => changeMode(status?.mode === 'off' ? 'auto' : 'off')}>
			<StatusIcon on={status.mode !== 'off'} image="power" size="48px"></StatusIcon>
		</GridElement>
		<GridElement
			col={1}
			row={2}
			click={status.mode == 'boil'
				? undefined
				: () => {
						changeMode('boil')
					}}
		>
			<StatusIcon on={status.mode === 'boil'} image="boil" text="Boil" size="48px"></StatusIcon>
		</GridElement>
		<GridElement col={1} row={3} click={togglePump}>
			<StatusIcon on={status.pump} image="pump" text="Pump" size="48px"></StatusIcon>
		</GridElement>
		<GridElement col={1} row={4}>
			<div>Temperature</div>
			<span class="text-xl"
				>{status.temperature == null ? 'Error' : formatTemp(status.temperature)}</span
			>
		</GridElement>
		<GridElement col={2} row={4}>
			<EditableNumber
				name="Setpoint"
				showName={false}
				suffix="°C"
				nonZero
				min={0}
				max={100}
				bind:value={status.setpoint}
				updateFunction={setSetpoint}
				afterUpdate={update}
				confirmationMessage={status?.mode === 'tuning' ? cancelTuningMessage : undefined}
				showSuccessMessage={false}
			>
				<div>Setpoint</div>
				<span class="text-xl {status.mode != 'auto' ? 'text-neutral-400' : ''}"
					>{status.setpoint}°C</span
				>
			</EditableNumber>
		</GridElement>
		<GridElement col={3} row={4}>
			<EditableNumber
				name="Duty cycle"
				showName={false}
				suffix="%"
				min={0}
				max={100}
				bind:value={status.dutyCycle}
				updateFunction={setDutyCycle}
				afterUpdate={update}
				confirmationMessage={status?.mode === 'tuning' ? cancelTuningMessage : undefined}
				showSuccessMessage={false}
			>
				<div>Duty cycle</div>
				<span class="text-xl {status.mode != 'manual' ? 'text-neutral-400' : ''}"
					>{Math.round(status.dutyCycle)}%</span
				>
			</EditableNumber>
		</GridElement>
		<GridElement col={4} endCol={7} row={4}><div class="text-2xl">{modeText}</div></GridElement>
		<GridElement col={2} endCol={7} row={1} endRow={3}
			><div class="pl-3 pr-3"><canvas id="chart"></canvas></div></GridElement
		>
	</Grid>
{/if}

<style>
</style>
