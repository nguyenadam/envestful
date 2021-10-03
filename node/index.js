const sass = require('sass');
const fs = require('fs')
const CleanCSS = require('clean-css');


const data = `
  @import "node_modules/bulma/sass/utilities/_all.sass";
  @import "node_modules/bulma/sass/grid/columns.sass";

`

const {
  css, 
  stats: {includedFiles}
} = sass.renderSync({
  // file: "styles.sass",
  data
});

const {
  styles, 
  stats: {
    efficiency,
    minifiedSize,
    originalSize
  }
} = new CleanCSS().minify(css);

console.log("included files: ")
includedFiles.forEach(x => console.log(x.split("node_modules/bulma/sass/")[1]))


fs.writeFileSync("output.css", styles)

