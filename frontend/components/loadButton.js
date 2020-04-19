import React, { useCallback } from 'react';
import Button from '@material-ui/core/Button';
import { observer } from 'mobx-react';
import { useStores } from './rootStore';


export const DeleteButton = observer(({ element }) => {
    const { sourcesStore } = useStores();
    const onClick = useCallback(() => sourcesStore.deleteSource(element), []);
    return (
    <Button onClick={onClick}>
        Delete: {sourcesStore.state}
    </Button>
    );
});

export default observer((props) => {
    const { sourcesStore } = useStores();
    return (
    <Button {...props} onClick={sourcesStore.listSources}>
        Retrieve public data: {sourcesStore.state}
    </Button>
    );
});
