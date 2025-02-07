<script lang="ts">
	import { Chart } from 'chart.js/auto'
	import { getJson, putWithParams } from '$lib/api/base-api'
	import LoadingScreen from '$lib/components/loading/LoadingScreen.svelte'
	import { onMount } from 'svelte'
	import { error, success } from '$lib/components/toast/toast-store.svelte'
	import ModeSelection from '$lib/components/mode-selection/ModeSelection.svelte'
	import EditableNumber from '$lib/components/input/EditableNumber.svelte'
	type Mode = 'off' | 'auto' | 'manual' | 'boil' | 'tuning'

	type Status = {
		mode: Mode
		pump: boolean
		temperature: number
		setpoint: number
		dutyCycle: number
		chartX: string[]
		chartTemperatureY: number[]
		chartSetpointY: number[]
		chartDutyCycleY: number[]
		boilAchieved: boolean
		autotunePeakCount?: number
	}

	let status: Status | undefined = $state()
	let chartObject: Chart
	let chartCanvas: HTMLCanvasElement

	const jou: number[] = []
	const x: string[] = []

	function setupChart() {
		chartObject = new Chart(chartCanvas, {
			type: 'line',
			data: {
				labels: x,
				datasets: [
					{
						label: 'Power',
						yAxisID: 'duty',
						data: jou,
					},
					{
						label: 'Setpoint',
						yAxisID: 'temp',
						data: jou,
					},
					{
						label: 'Temperature',
						yAxisID: 'temp',
						data: jou,
					},
				],
			},
			options: {
				animation: false,
				scales: {
					temp: {
						type: 'linear',
						position: 'left',
					},
					duty: {
						type: 'linear',
						position: 'right',
						min: 0,
						max: 100,
					},
				},
			},
		})
	}

	const update = () => {
		return getJson<Status>('/status')
			.then((result) => {
				status = result
				if (chartObject != null) {
					x.push('1')
					jou.push(1)
					chartObject.update()
				}
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
		updateInterval = setInterval(update, 1000)
		document.addEventListener('refreshData', update)
		return () => {
			clearInterval(updateInterval)
			document.removeEventListener('refreshData', update)
		}
	})

	const chart = (node: HTMLCanvasElement) => {
		$effect(() => {
			chartCanvas = node
			setupChart()
			return () => {
				chartObject.destroy()
			}
		})
	}
</script>

{#if status == null}
	<LoadingScreen />
	<!-- svelte-ignore a11y_no_static_element_interactions -->
{:else}
	<ModeSelection
		modes={['off', 'auto', 'manual', 'boil']}
		bind:active={status.mode}
		unselect
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
	<div class="h-50 w-2/6"><canvas use:chart></canvas></div>
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
