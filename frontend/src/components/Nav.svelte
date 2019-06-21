<script>
	import { onMount } from 'svelte';
	import Login from './Login.svelte';
	export let segment;
	let isLoggedIn;
	let buttonName = "Wait...";
	let unselectedClass;
	onMount(async () => {
		const { default: getAuth } = await import(`../utils/auth`);
		getAuth().then((auth) => {
			if (auth.isAuthenticated()) {
				isLoggedIn = true;
				unselectedClass = '';
				buttonName = 'Log Out';
			} else {
				isLoggedIn = false;
				unselectedClass = 'disabled';
				buttonName = 'Log In';
			}
		})
	});
</script>

<style>
	nav {
		border-bottom: 1px solid rgba(255,62,0,0.1);
		font-weight: 300;
		padding: 0 1em;
	}

	ul {
		margin: 0;
		padding: 0;
	}

	/* clearfix */
	ul::after {
		content: '';
		display: block;
		clear: both;
	}

	li {
		display: block;
		float: left;
	}

	.selected {
		position: relative;
		display: inline-block;
	}

	.selected::after {
		position: absolute;
		content: '';
		width: calc(100% - 1em);
		height: 2px;
		background-color: rgb(255,62,0);
		display: block;
		bottom: -1px;
	}

	.disabled {
		pointer-events: none;
		color: gray;
		cursor: default;
	}

	a {
		text-decoration: none;
		padding: 1em 0.5em;
		display: block;
	}
</style>

<nav>
	<ul>
		<li><a class='{segment === undefined ? "selected" : ""}' href='.'>Start</a></li>
		<li><a class='{segment === "monitor" ? "selected" : unselectedClass}' href='monitor'>Monitor</a></li>
		<li><a class='{segment === "trade" ? "selected" : unselectedClass}' href='trade'>Trade</a></li>
		<li>
			<Login let:onclick={onclick}>
				<button on:click={onclick}>{buttonName}</button>
			</Login>
		</li>
	</ul>
</nav>