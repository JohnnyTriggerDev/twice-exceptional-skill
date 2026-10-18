// Parse every ```mermaid block in the repo's Markdown files; exit 1 on a syntax error.
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';
const dom = new JSDOM('<!doctype html><html><body></body></html>');
globalThis.window = dom.window; globalThis.document = dom.window.document;
const { default: mermaid } = await import('mermaid');
const files = [];
const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) {
  if (e.name === '.git' || e.name === 'node_modules') continue;
  const p = path.join(d, e.name);
  e.isDirectory() ? walk(p) : p.endsWith('.md') && files.push(p);
} };
walk(process.argv[2] || '.');
let bad = 0, n = 0;
for (const f of files) {
  for (const m of fs.readFileSync(f, 'utf8').matchAll(/```mermaid\n([\s\S]*?)```/g)) {
    n++;
    try { await mermaid.parse(m[1]); } catch (e) { bad++; console.log(`${f}: ${e.message}`); }
  }
}
console.log(bad ? `${bad} of ${n} diagrams failed` : `OK: ${n} diagrams`);
process.exit(bad ? 1 : 0);
