<script>
import { onMount } from 'svelte';

let secondary = (e) => {};
let onClick = (e) => { 
	return secondary(e);
};

onMount(async () => {
	const { default: getAuth } = await import(`../utils/auth`);
	secondary = (e) => {
		getAuth().then((auth) => {
			auth.lock.show();
		});
	}
});
</script>

<div>
	<slot onclick={onClick}>
	</slot>
</div>
