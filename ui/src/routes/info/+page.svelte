<script lang="ts">
	import { getJson } from '$lib/api/base-api'
	import LoadingScreen from '$lib/components/loading/LoadingScreen.svelte'
	import { error } from '$lib/components/toast/toast-store.svelte'
	import dayjs from 'dayjs'
	import { onMount } from 'svelte'

	type Log = {
		millis: number
		text: string
	}
	type Info = {
		logs: Log[]
		cpuTemperature: number
		startMillis: number
	}
	let info: Info | undefined = $state()

	const update = () => {
		return getJson<Info>('/info')
			.then((result) => {
				info = result
			})
			.catch(() => {
				error('Error getting info!')
			})
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

{#if info == null}
	<LoadingScreen />
{:else}
	<div class="text-2xl">CPU temperature: {info.cpuTemperature}°C</div>
	<div class="text-2xl">
		Started on: {dayjs(info.startMillis).format('YYYY-MM-DD HH:mm:ss.SSS')}
	</div>
	<div class="mb-2 mt-6 text-2xl">Logs:</div>
	<div class="mb-3">
		{#each info.logs as log}
			<p>{dayjs(log.millis).format('HH:mm:ss.SSS')}: {log.text}</p>
		{/each}
	</div>
{/if}
