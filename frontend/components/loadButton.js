import React, { useContext } from 'react';
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react-lite'

import UsersContext from './Users/store';


export default observer((props) => {
    const store = useContext(UsersContext);
    return (
    <Button {...props} onClick={store.fetchProjects}>
        Retrieve public data: {store.state}
    </Button>
    );
});
