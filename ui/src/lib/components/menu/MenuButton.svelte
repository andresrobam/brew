<script lang="ts">
	import { page } from '$app/state'
	import { goto } from '$app/navigation'
	import type { MenuItem } from './types'
	interface Props {
		menuItem: MenuItem
	}

	let { menuItem }: Props = $props()

	let active: boolean = $derived.by(() => menuItem.route === page.url.pathname)

	function click() {
		goto(menuItem.route)
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
	class="block h-24 {active ? 'bg-gray-400' : 'cursor-pointer active:bg-gray-600'}"
	onclick={active ? () => {} : click}
>
	<!-- svelte-ignore a11y_missing_attribute -->
	<img class="size-full" src={menuItem.image} />
</div>

<style>
</style>
