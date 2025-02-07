<script lang="ts">
	import Menu from '$lib/components/menu/Menu.svelte'
	import Toasts from '$lib/components/toast/Toasts.svelte'
	import '../app.css'
	let { children } = $props()
</script>

<Toasts />
<div class="navbar">
	<Menu />
</div>
<div class="content pl-8 pt-8">
	{@render children()}
</div>

<style>
	.navbar {
		height: 100%;
		width: 100px;
		position: fixed;
		z-index: 1;
		top: 0;
		left: 0;
		background-color: #111;
		overflow-x: hidden;
	}
	.content {
		margin-left: 100px;
	}
</style>
