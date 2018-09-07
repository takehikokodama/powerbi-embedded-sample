var path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/powerbi_embedded_sample/static/src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve('src', 'powerbi_embedded_sample/static/', 'dist')
  }
};
