<script lang="ts" generics="T extends string">
	import type { Snippet } from 'svelte'
	import { error, success } from '../toast/toast-store.svelte'
	let {
		modes,
		active = $bindable(),
		unselect = false,
		dontShowActive = false,
		confirmationMessage,
		successMessage,
		errorMessage,
		updateFunction = Promise.resolve,
		afterUpdate,
		children,
	}: {
		modes: T[]
		active?: T
		unselect?: boolean
		dontShowActive?: boolean
		confirmationMessage?: string
		successMessage?: string
		errorMessage?: string
		updateFunction?: (value: T) => Promise<void>
		afterUpdate?: () => void
		children: Snippet
	} = $props()

	function select(mode: T) {
		if (confirmationMessage != null) {
			if (!confirm(confirmationMessage.replaceAll('{mode}', mode))) {
				return
			}
		}
		const previousMode = active
		active = mode
		updateFunction(active)
			.then(() => {
				if (successMessage != null) success(successMessage)
				if (afterUpdate != null) {
					afterUpdate()
				}

				if (unselect) {
					active = undefined
				}
			})
			.catch(() => {
				active = previousMode
				if (errorMessage != null) error(errorMessage)
			})
	}
</script>

<div>
	{@render children?.()}
	{#each modes as mode, i}
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			onclick={mode === active ? () => {} : () => select(mode)}
			class="inline-block p-2 {i == 0 ? 'rounded-l-xl' : ''} {i == modes.length - 1
				? 'rounded-r-xl'
				: ''} {dontShowActive
				? ''
				: mode === active
					? 'bg-sky-400'
					: 'inline-block cursor-pointer active:bg-sky-600'}"
		>
			{mode}
		</div>
	{/each}
</div>
