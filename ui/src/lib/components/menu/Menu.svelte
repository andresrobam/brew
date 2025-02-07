<script lang="ts">
	import MenuButton from './MenuButton.svelte'
	import type { MenuItem } from './types'
	import homeLogo from './images/home.svg'
	import settingLogo from './images/settings.svg'
	import infoLogo from './images/info.svg'

	const menuItems: MenuItem[] = [
		{ route: '/', image: homeLogo },
		{ route: '/settings', image: settingLogo },
		{ route: '/info', image: infoLogo },
	]
</script>

<div class="navbar z-10">
	{#each menuItems as menuItem}
		<MenuButton {menuItem} />
	{/each}
</div>
