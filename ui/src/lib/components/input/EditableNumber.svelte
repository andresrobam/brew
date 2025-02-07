<script lang="ts">
	import Keypad from './Keypad.svelte'
	import type { EditableNumberSettings } from './types'

	let {
		name,
		keepCapitalization,
		value = $bindable(),
		min,
		max,
		nonZero,
		updateFunction,
		afterUpdate,
		suffix,
	}: EditableNumberSettings = $props()
	let showKeypad: boolean = $state(false)
</script>

{#if showKeypad}
	<Keypad
		bind:value
		bind:show={showKeypad}
		{name}
		{keepCapitalization}
		{updateFunction}
		{afterUpdate}
		{suffix}
		{min}
		{max}
		{nonZero}
	/>
{/if}
<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="mb-4 table w-auto cursor-pointer text-3xl" onclick={() => (showKeypad = true)}>
	{#if name != null}
		<span class="mr-4">{name}: </span>
	{/if}
	<span>
		{value}{suffix ?? ''}
	</span>
</div>
