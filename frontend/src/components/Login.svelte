<script>
	import getAuth from '../utils/auth';
	// const getAuth = () => {
	// 	return {
	// 		lock: {
	// 			show: () => {
	// 				alert('hhhhnng!');
	// 			}
	// 		}
	// 	}
	// };
	const onClick = async (e) => {
		getAuth().then((auth) => {
			debugger;
			auth.lock.show();
		})
	}
</script>

<div>
	<slot onclick={onClick}>
	</slot>
</div>
