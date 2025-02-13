<script lang="ts">
	import Keypad from './Keypad.svelte'
	import type { EditableNumberSettings } from './types'

	let {
		name,
		showName = true,
		customClass,
		keepCapitalization,
		value = $bindable(),
		min,
		max,
		nonZero,
		updateFunction,
		afterUpdate,
		suffix,
		children,
		fillSlot = true,
		confirmationMessage,
		showSuccessMessage = true,
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
		{confirmationMessage}
		{showSuccessMessage}
	/>
{/if}
<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
{#if children != null}
	<div class={fillSlot ? 'size-full place-content-center' : ''} onclick={() => (showKeypad = true)}>
		{@render children?.()}
	</div>
{:else}
	<div
		class={customClass ?? 'mb-4 table w-auto cursor-pointer text-3xl'}
		onclick={() => (showKeypad = true)}
	>
		{#if showName && name != null}
			<span class="mr-4">{name}: </span>
		{/if}
		<span>
			{value}{suffix ?? ''}
		</span>
	</div>
{/if}
