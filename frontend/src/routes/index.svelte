<script>

</script>

<style>

	@import '../css/_variables.css';

	h1, figure, p {
		text-align: center;
		margin: 0 auto;
	}

	h1 {
		font-size: var(--fontSize);
		text-transform: uppercase;
		font-weight: 700;
		color: var(--mainColor);
		margin: 0 0 0.1rem 0;

	}

	figure {
		margin: 0 0 1em 0;
	}

	img {
		width: 100%;
		max-width: 400px;
		margin: 0 0 1em 0;
	}

	p {
		margin: 1em auto;
	}

	@media (min-width: 480px) {
		h1 {
			font-size: 4em;
		}
	}

	@mixin icon twitter {
    	background: url(twt.png);
	}
</style>

<svelte:head>
	<title>Sapper project template</title>
</svelte:head>

<h1 class="box">Great success!</h1>
<div class="rectangle">
	<a href="http://localhost:3000/#">fwefwef</a>
	<div class="icon is-twitter">hey</div>
</div>
<figure>
	<img alt='Borat' src='great-success.png'>
	<figcaption>HIGH FIVE!</figcaption>
</figure>

<p><strong>Try editing this file (src/routes/index.svelte) to test live reloading.</strong></p>
