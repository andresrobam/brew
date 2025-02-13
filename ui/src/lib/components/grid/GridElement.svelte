<script lang="ts">
	import type { Snippet } from 'svelte'

	let {
		col,
		row,
		endCol,
		endRow,
		click,
		children,
	}: {
		col: number
		row: number
		endCol?: number
		endRow?: number
		click?: () => void
		children: Snippet
	} = $props()

	function handleClick() {
		if (click != null) {
			click()
		}
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
	onclick={handleClick}
	class="block size-full min-h-32 place-content-center rounded-xl bg-white text-center shadow-lg"
	style="--col: {col}; --endCol: {(endCol ?? col) + 1}; --row: {row}; --endRow: {(endRow ?? row) +
		1}"
>
	{@render children?.()}
</div>

<style>
	div {
		grid-column-start: var(--col);
		grid-column-end: var(--endCol);
		grid-row-start: var(--row);
		grid-row-end: var(--endRow);
	}
</style>
