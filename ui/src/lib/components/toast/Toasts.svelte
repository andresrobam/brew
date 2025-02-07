<script lang="ts">
	import Toast from './Toast.svelte'
	import { getJson } from '$lib/api/base-api'
	import { removeToast, toasts, newToast, error } from './toast-store.svelte.js'
	import { onMount } from 'svelte'

	const update = () => {
		getJson<ToastInfo[]>('/messages')
			.then((result) => {
				if (result.length > 0) {
					result.forEach(newToast)
					document.dispatchEvent(new Event('refreshData'))
				}
			})
			.catch(() => {
				error('Error getting notification messages!')
			})
	}

	let updateInterval: number

	onMount(() => {
		updateInterval = setInterval(update, 1000)
		return () => {
			clearInterval(updateInterval)
		}
	})
</script>

<div class="pointer-events-none fixed z-30 size-full">
	{#each Object.values(toasts) as toast}
		<Toast {...toast} hide={() => removeToast(toast.id)} />
	{/each}
</div>
