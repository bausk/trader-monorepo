import { colors } from '@material-ui/core';


const white = '#FFFFFF';

export default {
  primary: {
    contrastText: white,
    dark: colors.blue[900],
    main: '#20A6F7',
    light: colors.blue[100],
  },
  secondary: {
    contrastText: colors.red.light,
    dark: colors.indigo[900],
    main: colors.indigo.A700,
    light: colors.indigo.A400,
  },
  error: {
    contrastText: white,
    dark: colors.red[900],
    main: '#FF1744',
    light: colors.red[400],
  },
  text: {
    primary: colors.blueGrey[900],
    secondary: colors.blueGrey[600],
    disabled: 'rgba(0, 0, 0, 0.38)',
    hint: 'rgba(0, 0, 0, 0.38)',
    link: colors.blue[600],
  },
  link: colors.blue[800],
  icon: colors.blueGrey[600],
  background: {
    default: '#F4F6F8',
    paper: white,
  },
  divider: colors.grey[200],
  new: {
    red: '#FF1744',
    black: '#263238',
    grey: '#546e7a',
    blue: '#40B6D7',
    green: '#4CAF50',
    greyCharts: '#A6B1BB',
  },
};
