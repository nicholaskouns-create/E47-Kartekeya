import {simulate,seededWeights,normalize,importRun,runCSV,runMarkdown,VALUES,COUNTS,EPSILON,VERSION} from './engine.mjs';
import {installInstrumentTelemetry} from '../shared/instrument-telemetry.js';
const telemetry=installInstrumentTelemetry({componentId:'e47-research-workbench',version:VERSION});
const $=id=>document.getElementById(id);
let bundle,run,activeView='dynamics',angleX=.45,angleY=.55,selectedFacet=0,drag=null,polygons=[],animation=0;
const fmt=x=>x===null||x===undefined?'undefined':Math.abs(x)<.0001&&x!==0?x.toExponential(3):Number(x).toPrecision(6);
function notice(message,error=false){$('notice').textContent=message;$('notice').classList.toggle('error',error);}
function guard(fn){return async(...args)=>{try{await fn(...args);}catch(error){notice(error.message,true);telemetry.reportFailure('interaction',error);}};}
function node(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function download(name,text,type='application/json'){
 const url=URL.createObjectURL(new Blob([text],{type})),a=node('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function currentInputs(){return {weights:[...$('weights').querySelectorAll('input')].map(x=>Number(x.value)),steps:Number($('steps').value),epsilon:$('epsilon').value==='imported'?Number($('epsilon').selectedOptions[0].dataset.epsilon):EPSILON*({optimal:1,small:.25,large:1.05}[$('epsilon').value]??1),mode:$('mode').value,horizon:Number($('horizon').value)};}
function setWeights(weights){[...$('weights').querySelectorAll('input')].forEach((x,i)=>{x.value=weights[i];});}
function preset(){
 const p=$('preset').value;
 $('seed-wrap').hidden=p!=='seeded';
 if(p==='isotropic')setWeights(COUNTS.map(x=>x/125));
 else if(p==='seeded')setWeights(seededWeights(Number($('seed').value)));
 else if(p==='selected')setWeights([0,0,25/47,0,0,22/47,0]);
 else if(p==='complement')setWeights(COUNTS.map((x,i)=>i===2||i===5?0:x/78));
}
function drawChart(canvas,series,{log=false,xLabel='iteration n',range=null}={}){
 const box=canvas.getBoundingClientRect();if(!box.width||!box.height)return;
 const dpr=window.devicePixelRatio||1;canvas.width=Math.round(box.width*dpr);canvas.height=Math.round(box.height*dpr);
 const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);const W=box.width,H=box.height,m={l:56,r:18,t:16,b:38};
 const values=series.flatMap(s=>s.values).filter(v=>v!==null&&Number.isFinite(v));
 const transform=v=>log?Math.log10(Math.max(v,1e-16)):v;
 let ymin=range?.[0]??(log?4*Math.floor(Math.min(...values.map(transform),0)/4):0),ymax=range?.[1]??(log?0:Math.max(1,...values));
 if(ymin===ymax)ymin=ymax-1;
 const py=v=>m.t+(ymax-transform(v))/(ymax-ymin)*(H-m.t-m.b),px=i=>m.l+i/Math.max(1,series[0].values.length-1)*(W-m.l-m.r);
 ctx.font='10px system-ui';ctx.lineWidth=1;
 for(let k=0;k<=4;k++){
  const y=m.t+k*(H-m.t-m.b)/4,v=ymax-k*(ymax-ymin)/4;
  ctx.strokeStyle='#253246';ctx.beginPath();ctx.moveTo(m.l,y);ctx.lineTo(W-m.r,y);ctx.stroke();ctx.fillStyle='#92a2b7';ctx.textAlign='right';ctx.fillText(log?`10^${v.toFixed(0)}`:v.toFixed(2),m.l-10,y+4);
 }
 ctx.textAlign='center';for(let k=0;k<=4;k++){const x=m.l+k*(W-m.l-m.r)/4;ctx.fillText(Number((k*(series[0].xMax??run?.inputs.steps??46)/4).toPrecision(3)).toString(),x,H-20);}
 ctx.fillText(xLabel,m.l+(W-m.l-m.r)/2,H-4);
 for(const s of series){ctx.strokeStyle=s.color;ctx.lineWidth=2;ctx.setLineDash(s.dashed?[5,5]:[]);ctx.beginPath();let started=false;s.values.forEach((v,i)=>{if(v===null||!Number.isFinite(v)){started=false;return;}if(started)ctx.lineTo(px(i),py(v));else ctx.moveTo(px(i),py(v));started=true;});ctx.stroke();}ctx.setLineDash([]);
}
function renderRun(){
 const last=run.records.at(-1),continuous=run.inputs.mode==='continuous';
 $('rho').textContent=fmt(run.rho);$('rho-label').textContent=continuous?'Discrete radius for configured ε':'Configured step · complement';
 $('final-error').textContent=fmt(last.error);$('final-occupancy').textContent=last.occupancy===null?'Undefined':(100*last.occupancy).toFixed(5)+'%';$('final-probability').textContent=fmt(last.probability);
 $('probability-label').textContent=continuous?'UNNORMALIZED NORM²':'FILTER SUCCESS PROBABILITY';$('run-label').textContent=continuous?'CONTINUOUS':'DISCRETE';
 const xMax=continuous?run.inputs.horizon:run.inputs.steps,xLabel=continuous?'scaled time τ = gap × t':'iteration n';
 drawChart($('convergence'),[{values:run.records.map(r=>r.error),color:'#74e1d0',xMax},{values:run.records.map(r=>r.bound),color:'#d7b879',dashed:true,xMax}],{log:true,xLabel});
 drawChart($('occupancy'),[{values:run.records.map(r=>r.occupancy),color:'#74e1d0',xMax}],{xLabel,range:[0,1]});
 $('samples').replaceChildren();
 const indices=[...new Set([0,1,Math.round(run.inputs.steps*.05),Math.round(run.inputs.steps*.25),Math.round(run.inputs.steps*.5),run.inputs.steps])].sort((a,b)=>a-b);
 for(const i of indices){const r=run.records[i],tr=node('tr');for(const v of [r.n,fmt(r.tau),fmt(r.error),fmt(r.bound),fmt(r.occupancy),fmt(r.probability)])tr.append(node('td',v));$('samples').append(tr);}
 notice(run.kernel_weight===0?'Run complete. No initial selected component: conditional fidelity is undefined.':`Run complete · ${run.inputs.steps} ${continuous?'samples':'iterations'} · initial selected weight ${fmt(run.kernel_weight)} · computed in this browser.`);
}
function execute(){run=simulate(currentInputs());renderRun();}
function barRow(label,value,max,selected=false){const row=node('div',undefined,'bar-row'),track=node('div',undefined,'bar-track'),fill=node('div',undefined,'bar-fill'+(selected?' selected':''));fill.style.width=`${value/max*100}%`;track.append(fill);row.append(node('span',label),track,node('span',String(value)));return row;}
function metric(container,label,value){const e=node('div',undefined,'metric');e.append(node('span',label),node('b',String(value)));container.append(e);}
function ledger(){
 $('checks').replaceChildren();const validation=bundle.validation;
 $('validation-summary').replaceChildren(node('p',`${validation.checks.filter(x=>x.passed).length} / ${validation.checks.length} saved matrix and geometry checks passed.`,validation.status==='pass'?'pass':'fail'));
 for(const check of validation.checks){const tr=node('tr');tr.append(node('td',check.name),node('td',fmt(check.residual)),node('td',fmt(check.tolerance)),node('td',check.passed?'PASS':'FAIL',check.passed?'pass':'fail'));$('checks').append(tr);}
 const audit=bundle.comparison_audit;$('audit-text').textContent=`The supplied CSV reports ρ = ${audit.reported_rho}; the optimal canonical filter gives ρ = ${fmt(audit.canonical_rho)}. A small-step interpretation would imply ε ≈ ${fmt(audit.inferred_small_step)}, but the generator and step were not supplied. This is an inference, not a verified repair of the source data.`;
 for(const source of bundle.sources.sources){const tr=node('tr');tr.append(node('td',source.file),node('td',source.sha256,'hash'));$('sources').append(tr);}
}
function verify(){
 const reference=bundle.reference_run,computed=simulate(reference.inputs);
 const differences=computed.records.map((r,i)=>Math.abs(r.error-reference.records[i].error));
 const residual=Math.max(...differences);
 const bounds=computed.records.every(r=>r.error<=r.bound+1e-12);
 const monotone=computed.records.every((r,i)=>i===0||r.occupancy+1e-12>=computed.records[i-1].occupancy);
 if(residual>1e-12||!bounds||!monotone)throw new Error('Browser/Python parity check failed.');
 notice(`Browser verification passed: Python reference parity (max error residual ${fmt(residual)}), decay bounds, and monotone occupancy. Saved matrix checks were not rerun in the browser.`);
}
function facetInspector(){const g=bundle.geometry,label=g.labels[selectedFacet];$('facet').value=String(selectedFacet);$('facet-info').replaceChildren();metric($('facet-info'),'Spin J',label.J);metric($('facet-info'),'Intermediate spin j₁₂',label.j12);metric($('facet-info'),'Magnetic index m',label.m);metric($('facet-info'),'Face vertices',g.faces[selectedFacet].length);metric($('facet-info'),'Adjacent faces',g.adjacency[selectedFacet].reduce((a,b)=>a+b,0));}
function rotatePoint(p){const [x,y,z]=p,c=Math.cos(angleY),s=Math.sin(angleY),u=x*c+z*s,v=-x*s+z*c;return [u,y*Math.cos(angleX)-v*Math.sin(angleX),y*Math.sin(angleX)+v*Math.cos(angleX)];}
function drawCrystal(){
 if(!bundle||activeView!=='geometry')return;
 const canvas=$('crystal'),box=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;canvas.width=box.width*dpr;canvas.height=box.height*dpr;
 const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);const g=bundle.geometry,R=g.metrics.radius_max,scale=Math.min(box.width,box.height)*.34/R;
 const pts=g.vertices.map(p=>rotatePoint(p)),screen=pts.map(([x,y,z])=>[box.width/2+x*scale,box.height/2-y*scale,z]);
 polygons=g.faces.map((ids,i)=>({i,points:ids.map(k=>screen[k]),depth:ids.reduce((a,k)=>a+pts[k][2],0)/ids.length,normal:rotatePoint(g.normals[i])})).sort((a,b)=>a.depth-b.depth);
 for(const f of polygons){const light=.35+.5*Math.max(0,f.normal[2]),selected=f.i===selectedFacet;ctx.fillStyle=selected?'#d7b879':g.labels[f.i].J===2?`rgba(81,${Math.round(130+80*light)},${Math.round(130+70*light)},1)`:`rgba(${Math.round(53+45*light)},${Math.round(76+50*light)},${Math.round(113+65*light)},1)`;ctx.beginPath();f.points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fill();if($('wireframe').checked||selected){ctx.strokeStyle=selected?'#fff0c4':'#132b38';ctx.lineWidth=selected?1.8:.8;ctx.stroke();}}
 ctx.fillStyle='#91a0b3';ctx.font='10px system-ui';ctx.fillText('25 J=2 faces / 22 J=5 faces',18,box.height-18);
}
function tick(){animation=0;if($('rotate').checked&&activeView==='geometry'&&!matchMedia('(prefers-reduced-motion: reduce)').matches){angleY+=.006;drawCrystal();animation=requestAnimationFrame(tick);}}
function showView(view){
 const names={dynamics:['Spectral dynamics','A precise view into the 47-dimensional invariant subspace.'],geometry:['Crystal geometry','Inspect the halfspace construction, its facets, and face adjacency.'],validation:['Validation ledger','Trace each displayed invariant to an inspectable numerical reconstruction.'],workspace:['Research workspace','Connect experiments to your code, documents, context, and next actions.']};
 if(!names[view])view='dynamics';activeView=view;for(const e of document.querySelectorAll('.view'))e.hidden=e.id!==view;
 for(const e of document.querySelectorAll('nav button')){e.classList.toggle('active',e.dataset.view===view);e.setAttribute('aria-current',e.dataset.view===view?'page':'false');}
 $('view-title').textContent=names[view][0];$('view-description').textContent=names[view][1];history.replaceState(null,'',`#${view}`);
 if(view==='dynamics'&&run)renderRun();if(view==='geometry'){drawCrystal();drawChart($('laplacian'),[{values:bundle.geometry.laplacian_spectrum,color:'#74e1d0',xMax:46}],{xLabel:'ordered eigenvalue index'});if(!animation)tick();}
}
async function init(){
 const response=await fetch('./data.json');if(!response.ok)throw new Error(`Numerical bundle unavailable (HTTP ${response.status}).`);bundle=await response.json();
 if(bundle.schema!=='E47-WORKBENCH-BUNDLE-1.0'||bundle.validation.status!=='pass')throw new Error('The numerical bundle is invalid or contains failed checks.');
 for(let i=0;i<7;i++){const label=node('label',`J=${i} · C=${VALUES[i]}`),input=node('input');input.type='number';input.min='0';input.step='any';input.setAttribute('aria-label',`Sector J ${i} initial weight`);input.addEventListener('input',()=>{$('preset').value='custom';$('seed-wrap').hidden=true;});label.append(input);$('weights').append(label);$('sector-bars').append(barRow(`J = ${i}`,COUNTS[i],28,i===2||i===5));}
 preset();ledger();
 const g=bundle.geometry;for(let i=0;i<47;i++){const option=node('option',`Facet ${i+1} · J=${g.labels[i].J} · m=${g.labels[i].m}`);option.value=i;$('facet').append(option);}facetInspector();
 for(const [label,value] of [['Vertices',g.vertices.length],['Edges',g.edge_count],['Faces',g.faces.length],['Euler V − E + F',g.euler],['Volume',fmt(g.metrics.volume)],['Area',fmt(g.metrics.area)],['Sphericity',fmt(g.metrics.sphericity)]])metric($('geometry-metrics'),label,value);
 for(const [degree,count] of Object.entries(g.face_histogram))$('face-histogram').append(barRow(`${degree} edges`,count,Math.max(...Object.values(g.face_histogram)),false));
 const workspace=await fetch('./workspace.json');if(!workspace.ok)throw new Error('Workspace destinations unavailable.');const links=await workspace.json();
 for(const item of links.destinations){const a=node('a',undefined,'workspace-card');const url=new URL(item.url);if(url.protocol!=='https:')continue;a.href=url.href;a.target='_blank';a.rel='noopener noreferrer';a.append(node('div',item.platform,'eyebrow'),node('h2',item.title),node('p',item.description),node('small','Open research record ↗'));$('workspace-links').append(a);}
 run=simulate(currentInputs());showView(location.hash.slice(1)||'dynamics');renderRun();
}
for(const button of document.querySelectorAll('nav button'))button.addEventListener('click',guard(()=>showView(button.dataset.view)));
$('run').addEventListener('click',guard(execute));$('preset').addEventListener('change',guard(()=>{preset();execute();}));$('seed').addEventListener('change',guard(()=>{preset();execute();}));
$('steps').addEventListener('input',()=>{$('steps-output').value=$('steps').value;});
$('mode').addEventListener('change',guard(()=>{$('epsilon-wrap').hidden=$('mode').value==='continuous';$('horizon-wrap').hidden=$('mode').value==='discrete';execute();}));
$('export-json').addEventListener('click',guard(()=>{if(!run)throw new Error('Run an experiment first.');download('e47-experiment.json',JSON.stringify({...run,exported_at:new Date().toISOString()},null,2));}));
$('export-csv').addEventListener('click',guard(()=>download('e47-samples.csv',runCSV(run),'text/csv')));
$('export-md').addEventListener('click',guard(()=>download('e47-research-note.md',runMarkdown(run),'text/markdown')));
$('import-file').addEventListener('change',guard(async()=>{const file=$('import-file').files[0];if(!file)return;if(file.size>2_000_000)throw new Error('Run file exceeds 2 MB.');const imported=importRun(await file.text());run=imported;setWeights(run.inputs.weights);$('preset').value='custom';$('seed-wrap').hidden=true;$('mode').value=run.inputs.mode;$('steps').value=run.inputs.steps;$('steps-output').value=run.inputs.steps;$('horizon').value=run.inputs.horizon;$('epsilon-wrap').hidden=run.inputs.mode==='continuous';$('horizon-wrap').hidden=run.inputs.mode==='discrete';const multiplier=run.inputs.epsilon/EPSILON;const entry=Object.entries({optimal:1,small:.25,large:1.05}).find(([,v])=>Math.abs(v-multiplier)<1e-12);if(entry)$('epsilon').value=entry[0];else {let option=$('epsilon').querySelector('[value="imported"]');if(!option){option=node('option');option.value='imported';$('epsilon').append(option);}option.textContent=`Imported ε · ${run.inputs.epsilon}`;option.dataset.epsilon=run.inputs.epsilon;$('epsilon').value='imported';}renderRun();$('import-file').value='';}));
$('verify').addEventListener('click',guard(verify));$('facet').addEventListener('change',()=>{selectedFacet=Number($('facet').value);facetInspector();drawCrystal();});
$('wireframe').addEventListener('change',drawCrystal);$('rotate').addEventListener('change',()=>{if(!animation)tick();});$('reset-camera').addEventListener('click',()=>{angleX=.45;angleY=.55;drawCrystal();});
$('crystal').addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY};$('crystal').setPointerCapture(e.pointerId);});
$('crystal').addEventListener('pointermove',e=>{if(!drag)return;angleY+=(e.clientX-drag.x)*.01;angleX+=(e.clientY-drag.y)*.01;drag.x=e.clientX;drag.y=e.clientY;drawCrystal();});
$('crystal').addEventListener('pointerup',e=>{if(drag&&Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)<5){const rect=$('crystal').getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top;for(const f of [...polygons].reverse()){let inside=false;for(let i=0,j=f.points.length-1;i<f.points.length;j=i++){const [xi,yi]=f.points[i],[xj,yj]=f.points[j];if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)inside=!inside;}if(inside){selectedFacet=f.i;facetInspector();break;}}}drag=null;drawCrystal();});
$('crystal').addEventListener('pointercancel',()=>{drag=null;});
$('crystal').addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();angleY+=(e.key==='ArrowRight'?.1:e.key==='ArrowLeft'?-.1:0);angleX+=(e.key==='ArrowDown'?.1:e.key==='ArrowUp'?-.1:0);drawCrystal();}});
$('export-obj').addEventListener('click',guard(()=>{const g=bundle.geometry;download('e47-47face-crystal.obj',['# E47 workbench geometry E1; polygon face mapping',...g.vertices.map(p=>'v '+p.join(' ')),...g.faces.map(f=>'f '+f.map(i=>i+1).join(' '))].join('\n')+'\n','text/plain');}));
window.addEventListener('resize',()=>{if(activeView==='dynamics'&&run)renderRun();if(activeView==='geometry'){drawCrystal();drawChart($('laplacian'),[{values:bundle.geometry.laplacian_spectrum,color:'#74e1d0',xMax:46}],{xLabel:'ordered eigenvalue index'});}});
window.addEventListener('hashchange',guard(()=>{if(bundle)showView(location.hash.slice(1));}));
guard(init)();
