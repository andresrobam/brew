<script lang="ts">
	import Boil from '$lib/components/main/images/Boil.svelte'
	import Power from '$lib/components/main/images/Power.svelte'
	import Pump from '$lib/components/main/images/Pump.svelte'

	let {
		on,
		text,
		image,
		size,
	}: { on: boolean; text?: string; image: 'boil' | 'power' | 'pump'; size?: string } = $props()

	let Image = $derived.by(() => {
		switch (image) {
			case 'boil':
				return Boil
			case 'power':
				return Power
			case 'pump':
				return Pump
		}
	})
</script>

<div>
	{text}
	<div class="ml-auto mr-auto table">
		<Image color={on ? 'green' : 'red'} {size} />
	</div>
</div>
