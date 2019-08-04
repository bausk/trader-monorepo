require('dotenv').config();
const path = require('path');
const Dotenv = require('dotenv-webpack');
const withCSS = require('@zeit/next-css');
const withSass = require('@zeit/next-sass');

const dev = process.env.NODE_ENV === 'development';
module.exports = withCSS({
  ...withSass({
    target: 'serverless',
    webpack: (config) => {
      config.plugins = config.plugins || [];
      config.plugins = [
        ...config.plugins,
        new Dotenv({
          path: path.join(__dirname, dev ? '.env' : 'production.env'),
          systemvars: true
        })
      ];
      return config;
    }
  }),
  cssModules: true
});
