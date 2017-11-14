const webpack = require("webpack");
const ExtractTextPlugin = require("extract-text-webpack-plugin");

const config = {
    entry:  __dirname + "/js/index.js",
    output: {
        path: __dirname + "/dist",
        filename: "bundle.js",
    },
    resolve: {
        extensions: [".js", ".es6", ".css", ".sass"]
    },
    module: {
        rules: [
            {
                test: /\.sass$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: ["css-loader", "sass-loader"]
                })
            }
        ],
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "jshint-loader"
            },
            {
                test: /\.es6$/,
                exclude: /node_modules/,
                loader: "babel-loader",
                query: {
                    presets: ["es2015"]
                }
            }
        ]
    },
    plugins: [
        new ExtractTextPlugin({
            filename: "style.css",
            allChunks: true
        })
    ],
};
module.exports = config;
