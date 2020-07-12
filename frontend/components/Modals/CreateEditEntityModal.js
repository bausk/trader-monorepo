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


export default function CreateEditEntityModal({ open, onClose, onSubmit, sources }) {
    const classes = useStyles();

    const handleClose = () => {
        onClose(false);
    };

    const [name, setName] = React.useState('Unnamed');
    const handleNameChange = (event) => {
      setName(event.target.value);
    };
    const [pls, setPLS] = React.useState("");
    const handlePLSChange = event => {
        setPLS(event.target.value);
    };
    const [sls, setSLS] = React.useState("");
    const handleSLSChange = event => {
        setSLS(event.target.value);
    };
    const [pbs, setPBS] = React.useState("");
    const handlePBSChange = event => {
        setPBS(event.target.value);
    };
    const [sbs, setSBS] = React.useState("");
    const handleSBSChange = event => {
        setSBS(event.target.value);
    };

    const handleSubmit = () => {
        onSubmit({
            name,
            primary_live_source_id: pls || undefined,
            secondary_live_source_id: sls || undefined,
            primary_backtest_source_id: pbs || undefined,
            secondary_backtest_source_id: sbs || undefined,
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
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Primary Live Source</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={pls}
                        onChange={handlePLSChange}
                        label="PLS"
                    >
                        <MenuItem value={""}>
                            <em>None</em>
                        </MenuItem>
                        {sources?.map(s => (
                            <MenuItem key={s.id} value={s.id}>{s.id} - {s.name}</MenuItem>
                        ))
                        }
                    </Select>
                </FormControl>
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Secondary Live Source</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={sls}
                        onChange={handleSLSChange}
                        label="SLS"
                    >
                        <MenuItem value={""}>
                            <em>None</em>
                        </MenuItem>
                        {sources?.map(s => (
                            <MenuItem key={s.id} value={s.id}>{s.id} - {s.name}</MenuItem>
                        ))
                        }
                    </Select>
                </FormControl>
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Primary Backtest Source</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={pbs}
                        onChange={handlePBSChange}
                        label="PBS"
                    >
                        <MenuItem value={""}>
                            <em>None</em>
                        </MenuItem>
                        {sources?.map(s => (
                            <MenuItem key={s.id} value={s.id}>{s.id} - {s.name}</MenuItem>
                        ))
                        }
                    </Select>
                </FormControl>
                <FormControl className={classes.formControl}>
                    <InputLabel id="demo-simple-select-outlined-label">Secondary Backtest Source</InputLabel>
                    <Select
                        margin="dense"
                        labelId="demo-simple-select-outlined-label"
                        id="demo-simple-select-outlined"
                        value={sbs}
                        onChange={handleSBSChange}
                        label="SBS"
                    >
                        <MenuItem value={""}>
                            <em>None</em>
                        </MenuItem>
                        {sources?.map(s => (
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
