<script>
import { onMount } from 'svelte';

let onClick;

onMount(async () => {
	const getAuth = await import(`../utils/auth`);
	onClick = (e) => {
		getAuth().then((auth) => {
			debugger;
			auth.lock.show();
		});
	}
});
	//import getAuth from '../utils/auth';
	// const getAuth = () => {
	// 	return {
	// 		lock: {
	// 			show: () => {
	// 				alert('hhhhnng!');
	// 			}
	// 		}
	// 	}
	// };
</script>

<div on:click={onClick}>
	click me
	<!-- <slot onclick={onClick}>
	</slot> -->
</div>
