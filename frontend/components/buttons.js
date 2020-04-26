import React, { useCallback } from 'react';
import Button from '@material-ui/core/Button';
import IconButton from "@material-ui/core/IconButton";
import DeleteIcon from "@material-ui/icons/Delete";
import { observer } from 'mobx-react';


export const DeleteButton = observer(({ element, mutate, store }) => {
    const onClick = useCallback(() => {
        mutate(async (prev) => {
            return prev.filter(el => el.id !== element.id);
        }, false);
        mutate(store.delete(element));
    }, [store, element, mutate]);
    return (
        <IconButton
            onClick={onClick}
            color="inherit"
            aria-label="delete item"
            disabled={element.id === undefined}
        >
            <DeleteIcon />
        </IconButton>
    );
});


export default observer(({ element, mutate, store }) => {
    return (
    <Button onClick={() => {}}>
        Retrieve public data:
    </Button>
    );
});
