const sls = require('serverless-http');
const binaryMimeTypes = require('./binaryMimeTypes');
const express = require('express');
const compression = require('compression');
const app = express();

const getPage = page => require(`./.next/serverless/pages/${page}`).render;
app.get("/", getPage("index"));

// Doesn't work when deployed without these 2 lines
app.use("/_next/static", express.static("./.next/static"));
app.use("/static", express.static("./static"));
app.use(compression());

// 404 handler
app.get("*", require("./.next/serverless/pages/_error").render);

module.exports.server = sls(app, {
  binary: binaryMimeTypes
});
