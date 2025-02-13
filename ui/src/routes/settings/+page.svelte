<script lang="ts">
	import { getJson, putWithParams } from '$lib/api/base-api'
	import EditableNumber from '$lib/components/input/EditableNumber.svelte'
	import LoadingScreen from '$lib/components/loading/LoadingScreen.svelte'
	import { onMount } from 'svelte'
	import { error } from '$lib/components/toast/toast-store.svelte'
	import ModeSelection from '$lib/components/mode-selection/ModeSelection.svelte'

	type TuningMode =
		| 'ziegler-nichols'
		| 'tyreus-luyben'
		| 'ciancone-marlin'
		| 'pessen-integral'
		| 'some-overshoot'
		| 'no-overshoot'

	type PIDMultipliers = {
		p: number
		i: number
		d: number
	}

	type BoilSettings = {
		boilThreshold: number
		boilPower: number
	}

	type OtherSettings = {
		initialSetpoint: number
		fanPower: number
	}

	let pidMultipliers: PIDMultipliers | undefined = $state(undefined)
	let boilSettings: BoilSettings | undefined = $state(undefined)
	let otherSettings: OtherSettings | undefined = $state(undefined)

	function startTuning(tuningMode: TuningMode) {
		return putWithParams('/mode', { mode: 'tuning', tuningMode })
	}

	function updatePIDMultipliers() {
		return pidMultipliers == null
			? Promise.resolve()
			: putWithParams('/settings/pid', pidMultipliers)
	}

	function updateBoilSettings() {
		return boilSettings == null ? Promise.resolve() : putWithParams('/settings/boil', boilSettings)
	}

	function updateOtherSettings() {
		return otherSettings == null
			? Promise.resolve()
			: putWithParams('/settings/other', otherSettings)
	}

	function getPIDMultipliers() {
		getJson<PIDMultipliers>('/settings/pid')
			.then((result) => {
				pidMultipliers = result
			})
			.catch(() => {
				error('Error getting PID multipliers!')
			})
	}

	function getBoilSettings() {
		getJson<BoilSettings>('/settings/boil')
			.then((result) => {
				boilSettings = result
			})
			.catch(() => {
				error('Error getting boil settings!')
			})
	}

	function getOtherSettings() {
		getJson<OtherSettings>('/settings/other')
			.then((result) => {
				otherSettings = result
			})
			.catch(() => {
				error('Error getting other settings!')
			})
	}

	onMount(() => {
		getPIDMultipliers()
		getBoilSettings()
		getOtherSettings()
		document.addEventListener('refreshData', getPIDMultipliers)

		return () => {
			document.removeEventListener('refreshData', getPIDMultipliers)
		}
	})
</script>

{#if pidMultipliers == null || otherSettings == null || boilSettings == null}
	<LoadingScreen />
{:else}
	<div class="mb-4 text-3xl font-bold">PID multipliers</div>
	<EditableNumber
		name="Kp"
		nonZero
		keepCapitalization
		min={0}
		bind:value={pidMultipliers.p}
		updateFunction={updatePIDMultipliers}
	/>
	<EditableNumber
		name="Ki"
		min={0}
		keepCapitalization
		bind:value={pidMultipliers.i}
		updateFunction={updatePIDMultipliers}
	/>
	<EditableNumber
		name="Kd"
		min={0}
		keepCapitalization
		bind:value={pidMultipliers.d}
		updateFunction={updatePIDMultipliers}
	/>
	<ModeSelection
		modes={[
			'ziegler-nichols',
			'tyreus-luyben',
			'ciancone-marlin',
			'pessen-integral',
			'some-overshoot',
			'no-overshoot',
		]}
		dontShowActive
		unselect
		successMessage="Started PID tuning!"
		errorMessage="Error starting PID tuning!"
		confirmationMessage={'Are you sure you want to start PID tuning with mode "{mode}"?'}
		updateFunction={startTuning}
	>
		<div class="mb-4 text-3xl font-bold">PID tuning</div>
	</ModeSelection>
	<div class="mb-4 mt-4 text-3xl font-bold">Boil settings</div>
	<EditableNumber
		name="Boil threshold"
		suffix="°C"
		nonZero
		min={0}
		bind:value={boilSettings.boilThreshold}
		updateFunction={updateBoilSettings}
	/>
	<EditableNumber
		name="Boil power"
		suffix="%"
		nonZero
		min={0}
		max={100}
		bind:value={boilSettings.boilPower}
		updateFunction={updateBoilSettings}
	/>
	<div class="mb-4 mt-4 text-3xl font-bold">Other settings</div>
	<EditableNumber
		name="Initial setpoint"
		suffix="°C"
		nonZero
		min={0}
		max={100}
		bind:value={otherSettings.initialSetpoint}
		updateFunction={updateOtherSettings}
	/>
	<EditableNumber
		name="Fan power"
		suffix="%"
		nonZero
		min={0}
		max={100}
		bind:value={otherSettings.fanPower}
		updateFunction={updateOtherSettings}
	/>
{/if}
