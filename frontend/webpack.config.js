const webpack = require('webpack');
const config = require('sapper/config/webpack.js');
const pkg = require('./package.json');
const autoPreprocess = require('svelte-preprocess');
const Dotenv = require('dotenv-webpack');

const preprocessOptions = {
	postcss: {
		plugins: [
			require('postcss-import'),
			require('postcss-define-property'),
			require('postcss-utilities'),
			require('postcss-mixins'),
			require('postcss-nested'),
			require('postcss-simple-vars'),
			require('postcss-preset-env')({
				stage: 0,
				autoprefixer: { grid: true },
				'nesting-rules': true
			}),
			require('postcss-normalize'),
			require('postcss-css-variables')
		]
	  }
};

const mode = process.env.NODE_ENV;
const dev = mode === 'development';

const extensions = ['.mjs', '.js', '.json', '.svelte', '.html'];
const mainFields = ['svelte', 'module', 'browser', 'main'];

const envPlugin = dev ?
	new Dotenv({}) :
	new Dotenv({
		path: './production.env'
	});

module.exports = {
	client: {
		entry: config.client.entry(),
		output: config.client.output(),
		resolve: { extensions, mainFields },
		module: {
			rules: [
				{
					test: /\.(svelte|html)$/,
					use: {
						loader: 'svelte-loader',
						options: {
							preprocess: autoPreprocess(preprocessOptions),
							dev,
							hydratable: true,
							hotReload: false // pending https://github.com/sveltejs/svelte/issues/2377
						}
					}
				}
			]
		},
		mode,
		plugins: [
			// pending https://github.com/sveltejs/svelte/issues/2377
			// dev && new webpack.HotModuleReplacementPlugin(),
			new webpack.DefinePlugin({
				'process.browser': true,
				'process.env.NODE_ENV': JSON.stringify(mode)
			}),
			envPlugin
		].filter(Boolean),
		devtool: dev && 'inline-source-map'
	},

	server: {
		entry: config.server.entry(),
		output: config.server.output(),
		target: 'node',
		resolve: { extensions, mainFields },
		externals: Object.keys(pkg.dependencies).concat('encoding'),
		module: {
			rules: [
				{
					test: /\.(svelte|html)$/,
					use: {
						loader: 'svelte-loader',
						options: {
							css: false,
							generate: 'ssr',
							dev
						}
					}
				}
			]
		},
		mode: process.env.NODE_ENV,
		plugins: [
			envPlugin
		],
		performance: {
			hints: false // it doesn't matter if server.js is large
		}
	},

	serviceworker: {
		entry: config.serviceworker.entry(),
		output: config.serviceworker.output(),
		mode: process.env.NODE_ENV
	}
};
