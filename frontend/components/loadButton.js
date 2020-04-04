import React from 'react';
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react';
import { useStores } from './rootStore';


export default observer((props) => {
    const { usersStore } = useStores();
    return (
    <Button {...props} onClick={usersStore.fetchProjects}>
        Retrieve public data: {usersStore.state}
    </Button>
    );
});
