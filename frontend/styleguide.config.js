module.exports = {
  components: 'src/components/**/*.{js,jsx,ts,tsx}',
  webpackConfig: require('./node_modules/react-scripts/config/webpack.config'),
  template: {
    head: {
      links: [
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap'
        }
      ]
    }
  },
  propsParser: require('react-docgen-typescript').parse,
  styleguideDir: 'styleguide-build'
};
