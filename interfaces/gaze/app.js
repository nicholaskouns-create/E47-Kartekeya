'use strict';
const $=id=>document.getElementById(id);let baseline=new Date(),selected='Polaris',positions=[];
const ns='http://www.w3.org/2000/svg';
function svg(tag,attrs,text){const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text)e.textContent=text;$('sky').appendChild(e);return e;}
function render(){try{
 const values=['lat','lon','height'].map(id=>{if(!$(id).value.trim())throw Error('Complete all location fields.');return Number($(id).value);});
 const offset=Number($('offset').value),unit=$('unit').value,date=new Date(+baseline+offset*(unit==='Hours'?3600000:86400000));
 positions=GazeSky.calculate(Astronomy,date,...values);$('error').textContent='';$('offsetLabel').textContent=`${offset>0?'+':''}${offset} ${unit.toLowerCase()}`;
 $('status').textContent=`${date.toISOString().replace('T',' · ')} | ${offset===0?'CURRENT SNAPSHOT':'OFFSET TIME-LOCK'} | ${values[0].toFixed(4)}° N, ${values[1].toFixed(4)}° E`;
 $('sky').replaceChildren();svg('circle',{cx:300,cy:275,r:225,fill:'#0d141e',stroke:'#405063'});
 for(const [r,t]of [[75,'60° alt'],[150,'30° alt'],[225,'Horizon']]){svg('circle',{cx:300,cy:275,r,fill:'none',stroke:'#263343'});svg('text',{x:305,y:275-r+16,fill:'#8795a8','font-size':11},t);}
 svg('path',{d:'M75 275H525 M300 50V500',stroke:'#263343'});
 for(const [x,y,t]of [[300,30,'N / 0°'],[562,280,'E'],[300,532,'S'],[35,280,'W']])svg('text',{x,y,fill:'#aebdcb','text-anchor':'middle','font-size':13},t);
 for(const p of positions.filter(p=>p.alt>0)){const a=p.az*Math.PI/180,r=(90-p.alt)*2.5,x=300+r*Math.sin(a),y=275-r*Math.cos(a),color=p.name==='Polaris'?'#ff9900':p.type==='Star'?'#5294e2':'#00ecff';
 const dot=svg('circle',{cx:x,cy:y,r:p.name===selected?8:5,fill:color,stroke:p.name===selected?'white':color});const title=document.createElementNS(ns,'title');title.textContent=`${p.name}: az ${p.az.toFixed(2)}°, alt ${p.alt.toFixed(2)}°`;dot.appendChild(title);svg('text',{x:x+9,y:y-10,fill:color,'font-size':12},p.name);}
 const pol=positions[0];$('polaris').textContent=`${pol.az.toFixed(2)}° az / ${pol.alt.toFixed(2)}° alt`;
 $('separation').textContent=GazeSky.separation(positions.find(p=>p.name==='Moon'),positions.find(p=>p.name==='Jupiter')).toFixed(2)+'°';
 $('targets').replaceChildren();for(const p of positions){const b=document.createElement('button');b.className='target'+(p.name===selected?' selected':'');b.textContent=p.name;b.setAttribute('aria-pressed',String(p.name===selected));const s=document.createElement('span');s.textContent=`${p.alt.toFixed(1)}° alt · ${p.alt>0?'ABOVE':'BELOW'}`;b.appendChild(s);b.onclick=()=>{selected=p.name;render();};$('targets').appendChild(b);}
 const p=positions.find(p=>p.name===selected);$('selected').textContent=`${p.name} · azimuth ${p.az.toFixed(3)}° · altitude ${p.alt.toFixed(3)}°`;
 }catch(e){$('error').textContent='Calculation unavailable: '+e.message;$('status').textContent='INPUT OR ENGINE ERROR';$('sky').replaceChildren();$('targets').replaceChildren();$('selected').textContent='';$('separation').textContent='—';$('polaris').textContent='—';}}
for(const id of ['lat','lon','height','unit','offset'])$(id).addEventListener('input',render);
$('now').onclick=()=>{baseline=new Date();$('offset').value=0;render();};render();
