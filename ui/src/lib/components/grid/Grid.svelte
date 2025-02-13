<script lang="ts">
	import type { Snippet } from 'svelte'

	let {
		cols,
		rows,
		children,
	}: {
		cols: number
		rows: number
		children?: Snippet
	} = $props()
</script>

<div class="grid size-full gap-3" style="--cols: {cols}; --rows: {rows}">
	{@render children?.()}
</div>

<style>
	.grid {
		grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
        grid-template-rows: repeat(var(--rows), minmax(0, 1fr));
	}
</style>
