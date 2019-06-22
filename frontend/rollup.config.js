import resolve from 'rollup-plugin-node-resolve';
import replace from 'rollup-plugin-replace';
import commonjs from 'rollup-plugin-commonjs';
import svelte from 'rollup-plugin-svelte';
import babel from 'rollup-plugin-babel';
import json from 'rollup-plugin-json';
import { terser } from 'rollup-plugin-terser';
import config from 'sapper/config/rollup.js';
import autoPreprocess from 'svelte-preprocess';
import dotenv from 'dotenv';

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
				browsers: 'last 2 versions',
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
dotenv.config(dev ? {} : { path: 'production.env' });
const legacy = !!process.env.SAPPER_LEGACY_BUILD;
const onwarn = (warning, onwarn) => (warning.code === 'CIRCULAR_DEPENDENCY' && warning.message.includes('/@sapper/')) || onwarn(warning);

export default {
	client: {
		input: config.client.input(),
		output: config.client.output(),
		plugins: [
			replace({
				'process.browser': true,
				'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
				'process.env.AUTH0_DOMAIN': JSON.stringify(process.env.AUTH0_DOMAIN),
				'process.env.AUTH0_CLIENT_ID': JSON.stringify(process.env.AUTH0_CLIENT_ID),
				'process.env.AUTH0_CALLBACK_URL' : JSON.stringify(process.env.AUTH0_CALLBACK_URL),
				'process.env.API_AUDIENCE': JSON.stringify(process.env.API_AUDIENCE)
			}),
			svelte({
				preprocess: autoPreprocess(preprocessOptions),
				dev,
				hydratable: true,
				emitCss: !dev
			}),
			resolve(),
			commonjs(),

			legacy && babel({
				extensions: ['.js', '.mjs', '.html', '.svelte'],
				runtimeHelpers: true,
				exclude: ['node_modules/@babel/**'],
				presets: [
					['@babel/preset-env', {
						targets: '> 0.25%, not dead',
						modules: false
					}]
				],
				plugins: [
					'@babel/plugin-syntax-dynamic-import',
					['@babel/plugin-transform-runtime', {
						useESModules: true
					}]
				]
			}),

			!dev && terser({
				module: true
			})
		],

		onwarn,
	},

	server: {
		input: config.server.input(),
		output: config.server.output(),
		plugins: [
			replace({
				'process.browser': false,
				'process.env.NODE_ENV': JSON.stringify(mode),
				'process.env.AUTH0_DOMAIN': JSON.stringify(process.env.AUTH0_DOMAIN),
				'process.env.AUTH0_CLIENT_ID': JSON.stringify(process.env.AUTH0_CLIENT_ID),
				'process.env.AUTH0_CALLBACK_URL' : JSON.stringify(process.env.AUTH0_CALLBACK_URL),
				'process.env.API_AUDIENCE': JSON.stringify(process.env.API_AUDIENCE)
			}),
			json(),
			svelte({
				generate: 'ssr',
				dev
			}),
			resolve(),
			commonjs()
		],
		external: ['cjs'].concat(
			require('module').builtinModules || Object.keys(process.binding('natives'))
		),

		onwarn,
	},

	serviceworker: {
		input: config.serviceworker.input(),
		output: config.serviceworker.output(),
		plugins: [
			resolve(),
			replace({
				'process.browser': true,
				'process.env.NODE_ENV': JSON.stringify(mode)
			}),
			commonjs(),
			!dev && terser()
		],

		onwarn,
	}
};
