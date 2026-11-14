// Builds dist/index.html from ../case-study/index.html: adds the document skeleton and enables live mode.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from "node:fs";

const src = readFileSync(new URL("../case-study/index.html", import.meta.url), "utf8");
const i = src.indexOf("<main>");
if (i < 0) throw new Error("case-study/index.html: no <main>");
const head = src.slice(0, i), body = src.slice(i);
const live = '<script>window.OPTOUT_API = "/api/classify";</script>\n';
const j = body.lastIndexOf("<script>");
if (j < 0) throw new Error("case-study/index.html: no widget script");
const html = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  + head + "</head>\n<body>\n" + body.slice(0, j) + live + body.slice(j) + "\n</body>\n</html>\n";
mkdirSync(new URL("./dist/", import.meta.url), { recursive: true });
writeFileSync(new URL("./dist/index.html", import.meta.url), html);
copyFileSync(new URL("./_headers", import.meta.url), new URL("./dist/_headers", import.meta.url));
console.log("built dist/index.html (" + html.length + " bytes)");
