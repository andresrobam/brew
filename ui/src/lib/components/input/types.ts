export type EditableNumberSettings = {
	name?: string
	keepCapitalization?: boolean
	value: number
	min?: number
	max?: number
	nonZero?: boolean
	suffix?: string
	updateFunction?: () => Promise<unknown>
	afterUpdate?: () => Promise<unknown>
}
