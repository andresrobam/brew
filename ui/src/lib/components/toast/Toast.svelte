<script lang="ts">
	const { text, style, hide }: ToastInfo & { hide: () => void } = $props()
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	onclick={hide}
	class="pointer-events-auto relative m-4 w-fit place-self-center rounded-2xl p-8 text-gray-200 shadow-lg shadow-gray-400 {style ==
	'success'
		? 'bg-lime-600'
		: ''} {style == 'error' ? 'bg-red-700' : ''}"
>
	<span>{text}</span>
</div>
