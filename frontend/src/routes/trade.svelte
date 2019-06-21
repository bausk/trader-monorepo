<script context="module">
	export function preload({ params, query }) {
		return this.fetch(`trade.json`).then(r => r.json()).then(data => {
			return { data };
		});
	}
</script>

<script>
	export let data;
</script>

<style>
	ul {
		margin: 0 0 1em 0;
		line-height: 1.5;
	}
</style>

<svelte:head>
	<title>Trade</title>
</svelte:head>

<h1>Secret</h1>

<h2>{data.message}</h2>