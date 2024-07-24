const webpack = require('webpack');

module.exports = {
  // ... other configurations ...
  mode: 'development',
  resolve: {
    fallback: {
      console: false,
    },
  },
  plugins: [
    new webpack.ProvidePlugin({
      process: 'process/browser',
    }),
  ],
};