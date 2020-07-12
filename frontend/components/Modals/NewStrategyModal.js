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
        minWidth: 280,
    },
    selectEmpty: {
        marginTop: theme.spacing(2)
    }
}));

const strategyTypesEnum = {
    'interexchangearbitrage': "Inter-Exchange Arbitrage",
    'signalbased': "Single Exchange",
};

export default function NewStrategyModal({ open, onClose, onSubmit, resources }) {
    const classes = useStyles();
    const handleClose = () => {
        onClose(false);
    };
    
    const [typename, setTypename] = React.useState(Object.keys(strategyTypesEnum)[0]);
    const handleTypeChange = event => {
        setTypename(event.target.value);
    };
    const [name, setName] = React.useState('Unnamed');
    const handleNameChange = (event) => {
      setName(event.target.value);
    };
    const [resource, setResource] = React.useState("");
    const handleResourceChange = event => {
        setResource(event.target.value);
    };
    const handleSubmit = () => {
        onSubmit({
            name,
            typename,
            resource_id: resource || undefined,
        });
        onClose(true);
    };
    return (
        <Dialog
            open={open}
            onClose={handleClose}
            aria-labelledby="form-dialog-title"
        >
            <DialogTitle id="form-dialog-title">Create Strategy</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Provide strategy name and type:
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
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Type</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={typename}
                        onChange={handleTypeChange}
                        label="Type"
                    >
                        {Object.entries(strategyTypesEnum).map(value => (
                            <MenuItem key={value[0]} value={value[0]}>{value[1]}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Source Assembly</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={resource}
                        onChange={handleResourceChange}
                        label="Source Assembly"
                    >
                        <MenuItem value={""}>
                            <em>None</em>
                        </MenuItem>
                        {resources?.map(s => (
                            <MenuItem key={s.id} value={s.id}>{s.id} - {s.name}</MenuItem>
                        ))
                        }
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
