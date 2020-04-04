import React, { useContext } from 'react';
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react';
import UsersContext from './Users/UsersStore';
import { useStores } from './rootStore';


export default observer((props) => {
    const store = useContext(UsersContext);
    const { userStore } = useStores();
    return (
    <Button {...props} onClick={userStore.addTodos}>
        Retrieve public data: {store.state}
    </Button>
    );
});
