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

<div
	class="block h-24 {active
		? 'bg-gray-400'
		: 'cursor-pointer active:bg-gray-600'}"
	onclick={active ? () => {} : click}
>
	<img class="size-full" src={menuItem.image} />
</div>

<style>
</style>
