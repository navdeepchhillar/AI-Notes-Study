module.exports = {
  style: {
    postcss: {
      mode: 'file',
    },
  },
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig.ignoreWarnings = [/Failed to parse source map/];
      return webpackConfig;
    },
  },
};