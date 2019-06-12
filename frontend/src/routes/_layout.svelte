<script>
	// import Auth0 from 'auth0-js';
	import Nav from '../components/Nav.svelte';
	
	// console.log(Auth0);
	// console.warn('Oy vey this is executed in many places');
	export let segment;
</script>

<style>
	main {
		position: relative;
		max-width: 56em;
		background-color: white;
		padding: 2em;
		margin: 0 auto;
		box-sizing: border-box;
	}
</style>

<Nav {segment}/>

<main>
	<slot></slot>
</main>