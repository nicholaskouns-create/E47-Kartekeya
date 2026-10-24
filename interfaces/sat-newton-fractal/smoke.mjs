import fs from 'node:fs';
const html=fs.readFileSync(new URL('./index.html',import.meta.url),'utf8');
for(const token of ['SAT → Newton → Basin Boundary','1.14990','MC-SAT-NEWTON-BOXDIM-20260922-001','sat_newton_boxdim.py']) if(!html.includes(token)) throw new Error('missing '+token);
console.log('sat-newton-fractal smoke PASS');
