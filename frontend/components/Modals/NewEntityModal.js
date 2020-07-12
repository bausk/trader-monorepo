import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import Select from "@material-ui/core/Select";

const useStyles = makeStyles(theme => ({
    formControl: {
        marginTop: theme.spacing(2),
        minWidth: 120,
    },
    selectEmpty: {
        marginTop: theme.spacing(2)
    }
}));

export default function NewEntityModal({ open, onClose, onSubmit }) {
    const classes = useStyles();
    const handleClose = () => {
        onClose(false);
    };
    
    const [sourceType, setSourceType] = React.useState("bigquery");
    const handleTypeChange = event => {
        setSourceType(event.target.value);
    };
    const [name, setName] = React.useState('Unnamed');
    const handleNameChange = (event) => {
      setName(event.target.value);
    };
    const [tableName, setTable] = React.useState('');
    const handleTableChange = (event) => {
        setTable(event.target.value);
    };
    const handleSubmit = () => {
        onSubmit({
            name,
            tableName,
            sourceType
        });
        onClose(true);
    };
    return (
        <Dialog
            open={open}
            onClose={handleClose}
            aria-labelledby="form-dialog-title"
        >
            <DialogTitle id="form-dialog-title">Create Source</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Provide name, source type and table:
                </DialogContentText>
                <TextField
                    autoFocus
                    margin="dense"
                    id="name"
                    label="Title"
                    type="text"
                    value={name}
                    onChange={handleNameChange}
                    fullWidth
                />
                <TextField
                    margin="dense"
                    id="tablename"
                    label="Table Name"
                    type="text"
                    value={tableName}
                    onChange={handleTableChange}
                    fullWidth
                />
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Type</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={sourceType}
                        onChange={handleTypeChange}
                        label="Type"
                    >
                        {/* <MenuItem value="">
                            <em>None</em>
                        </MenuItem> */}
                        <MenuItem value={'bigquery'}>BigQuery</MenuItem>
                        <MenuItem value={'kuna'}>KunaIO</MenuItem>
                        <MenuItem value={'cryptowatch'}>Cryptowatch</MenuItem>
                    </Select>
                </FormControl>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} color="primary">
                    Cancel
                </Button>
                <Button onClick={handleSubmit} color="primary">
                    Create
                </Button>
            </DialogActions>
        </Dialog>
    );
}
