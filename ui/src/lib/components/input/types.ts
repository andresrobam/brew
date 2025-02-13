import type { Snippet } from 'svelte'

export type EditableNumberSettings = {
	name?: string
	showName?: boolean
	customClass?: string
	keepCapitalization?: boolean
	value: number
	min?: number
	max?: number
	nonZero?: boolean
	suffix?: string
	updateFunction?: () => Promise<unknown>
	afterUpdate?: () => Promise<unknown>
	children?: Snippet
	fillSlot?: boolean
	confirmationMessage?: string
	showSuccessMessage?: boolean
}
