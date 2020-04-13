import React from 'react';
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react';
import { useStores } from './rootStore';


export default observer((props) => {
    const { sourcesStore } = useStores();
    return (
    <Button {...props} onClick={sourcesStore.listSources}>
        Retrieve public data: {sourcesStore.state}
    </Button>
    );
});
