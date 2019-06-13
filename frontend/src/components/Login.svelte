<script>
	import getAuth from '../utils/auth';
	const onClick = (e) => {
		const auth = getAuth();
		
	}
</script>

<div>
	<slot onclick={onClick}>
	</slot>
</div>
