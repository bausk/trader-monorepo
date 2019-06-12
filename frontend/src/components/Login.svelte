<script>
	import getAuth from '../utils/auth';
	const onClick = (e) => {
		window.alert("auth");
		console.log(window);
		const auth = getAuth();
	}
</script>

<div>
	<slot onclick={onClick}>
	</slot>
</div>
