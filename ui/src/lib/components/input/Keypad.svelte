<script lang="ts">
	import { error, success } from '../toast/toast-store.svelte'
	import type { EditableNumberSettings } from './types'

	let {
		name,
		keepCapitalization,
		value = $bindable(),
		show = $bindable(),
		min,
		max,
		nonZero,
		suffix,
		updateFunction,
		afterUpdate,
	}: EditableNumberSettings & { show: boolean } = $props()

	let valueString: string = $state(value.toString())

	let clicked: { [key: string]: number } = $state({})

	function unClick(text: string) {
		clicked = { ...clicked, [text]: (clicked[text] ?? 1) - 1 }
	}

	function makeClicked(text: string) {
		clicked = { ...clicked, [text]: (clicked[text] ?? 0) + 1 }
		setTimeout(() => unClick(text), 100)
	}

	function hide() {
		show = false
	}

	let isValid: boolean = $derived.by(() => {
		if (valueString === value.toString() || valueString.trim() === '') {
			return false
		}
		const valueNumber = Number(valueString)
		if (
			isNaN(valueNumber) ||
			(max != null && valueNumber > max) ||
			(min != null && valueNumber < min) ||
			(nonZero && valueNumber == 0)
		) {
			return false
		}
		return true
	})

	function add(addition: string): void {
		if (
			(addition === '.' && valueString.includes('.')) ||
			(addition === '0' && valueString === '0') ||
			valueString.length >= 15
		) {
			return
		}
		if (addition === '.' && valueString === '') {
			valueString = '0'
		}
		valueString += addition
	}

	function backspace(): void {
		if (valueString.length !== 0) {
			valueString = valueString.substring(0, valueString.length - 1)
		}
	}

	function clear(): void {
		valueString = ''
	}

	function submit(): void {
		if (!isValid) {
			return
		}
		const originalValue: number = value
		value = Number(valueString)
		if (updateFunction != null) {
			let valueNameInToast = name != null ? name : 'value'
			if (!keepCapitalization) {
				valueNameInToast =
					valueNameInToast.charAt(0).toLocaleLowerCase() + valueNameInToast.slice(1)
			}
			updateFunction()
				.then(() => {
					success(`Successfully updated ${valueNameInToast}!`)
					if (afterUpdate != null) {
						afterUpdate()
					}
				})
				.catch(() => {
					value = originalValue
					error(`Error when updating ${valueNameInToast}!`)
				})
		}

		hide()
	}

	function cancel(): void {
		valueString = value.toString()
		hide()
	}

	type KeypadButton = {
		action: () => void
		colspan?: number
		disabled?: boolean
		text: string
		image?: string
	}

	const buttons: KeypadButton[][] = $derived([
		[
			{ text: '1', action: () => add('1') },
			{ text: '2', action: () => add('2') },
			{ text: '3', action: () => add('3') },
		],
		[
			{ text: '4', action: () => add('4') },
			{ text: '5', action: () => add('5') },
			{ text: '6', action: () => add('6') },
		],
		[
			{ text: '7', action: () => add('7') },
			{ text: '8', action: () => add('8') },
			{ text: '9', action: () => add('9') },
		],
		[
			{ text: 'DEL', disabled: valueString.length === 0, action: backspace },
			{ text: '0', action: () => add('0') },
			{ text: '.', disabled: valueString.includes('.'), action: () => add('.') },
		],
		[
			{ text: 'CLR', disabled: valueString.length === 0, action: clear },
			{ text: 'ENTER', disabled: !isValid, action: submit, colspan: 2 },
		],
	])
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class="fixed left-0 top-0 z-20 flex size-full items-center justify-center bg-black/50"
	onclick={cancel}
>
	<div
		class="rounded-3xl bg-white"
		onclick={(e) => {
			e.stopPropagation()
		}}
	>
		<table class="m-10">
			<thead>
				<tr
					><th colspan="3">
						{#if name != null}<span class="block">{name}:</span>{/if}
						<span class="text-right">{valueString}{suffix ?? ''}&nbsp;</span>
					</th></tr
				>
			</thead>
			<tbody>
				{#each buttons as row}
					<tr>
						{#each row as button}
							<td
								class="size-16 rounded-xl text-center {button.disabled
									? ''
									: `cursor-pointer active:bg-slate-300 ${(clicked[button.text] ?? 0 > 0) ? 'bg-slate-300' : ''}`}"
								onclick={button.disabled
									? () => {}
									: () => {
											makeClicked(button.text)
											button.action()
										}}
								colspan={button.colspan ?? 1}
							>
								<div class="select-none {button.disabled ? 'opacity-50' : ''}">
									{#if button.image != null}
										<!-- svelte-ignore a11y_missing_attribute -->
										<img src={button.image} />
									{:else}
										{button.text}
									{/if}
								</div>
							</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
