<script context="module">
	export async function preload({ params, query }) {
		const { default: getAuth } = await import(`../utils/auth`);
		const auth = await getAuth();
		const token = auth.getAccessToken();
		const headers = { 'Authorization': `Bearer ${token}` };
		return this.fetch(`trade.json`, { headers }).then(r => r.json()).then(data => {
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