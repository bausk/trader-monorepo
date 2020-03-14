import { createMuiTheme } from '@material-ui/core/styles';
import palette from './palette';
import typography from './typography';
import overrides from './overrides';

const theme = {
    palette,
    typography,
    overrides, 
};

export default createMuiTheme(theme);
