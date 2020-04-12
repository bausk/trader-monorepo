const dotenv = require('dotenv')
dotenv.config()

module.exports = {
  // webpackDevMiddleware: (config) => {
  //   config.watchOptions = config.watchOptions || {};
  //   config.watchOptions.ignored = [
  //     // Don't watch _any_ files for changes
  //     /\.next/,
  //   ];
  //   return config;
  // },
  webpack(config) {
    config.resolve.modules.push(__dirname)
    return config;
  },
  env: {
    AUTH0_DOMAIN: process.env.AUTH0_DOMAIN,
    AUTH0_CLIENT_ID: process.env.AUTH0_CLIENT_ID,
    AUTH0_CLIENT_SECRET: process.env.AUTH0_CLIENT_SECRET,
    AUTH0_SCOPE: process.env.AUTH0_SCOPE,
    API_AUDIENCE: process.env.API_AUDIENCE,
    REDIRECT_URI:
      process.env.REDIRECT_URI || 'http://localhost:3000/api/callback',
    POST_LOGOUT_REDIRECT_URI:
      process.env.POST_LOGOUT_REDIRECT_URI || 'http://localhost:3000/',
    SESSION_COOKIE_SECRET: process.env.SESSION_COOKIE_SECRET,
    SESSION_COOKIE_LIFETIME: 7200, // 2 hours
    FRONTEND_ROOT:
      process.env.FRONTEND_ROOT || 'http://localhost:3000',
    BACKEND_ROOT:
      process.env.BACKEND_ROOT || 'http://localhost:5000',
  },
}
