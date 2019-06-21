<script>
import { onMount } from 'svelte';

let secondary = (e) => {};
let onClick = (e) => { 
	return secondary(e);
};

onMount(async () => {
	const { default: getAuth } = await import(`../utils/auth`);
	getAuth().then((auth) => {
		if (auth.isAuthenticated()) {
			secondary = (e) => {
				auth.logout();
			}
		} else {
			secondary = (e) => {
				auth.lock.show();
			}
		}
	});
});
</script>

<div>
	<slot onclick={onClick}>
	</slot>
</div>
