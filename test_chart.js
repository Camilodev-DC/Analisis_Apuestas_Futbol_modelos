const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const html = fs.readFileSync('pagina_web/index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable" });

dom.window.document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded");
  setTimeout(() => {
    const canvas = dom.window.document.getElementById('chart-clustering');
    console.log("Canvas exists:", !!canvas);
    if (dom.window.clusterChart) {
      console.log("Chart created!");
    } else {
      console.log("Chart NOT created");
    }
  }, 2000);
});
