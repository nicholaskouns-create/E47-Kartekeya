// MANTA-PYTHON-BRIDGE-1.0
const PYODIDE='https://cdn.jsdelivr.net/pyodide/v0.27.7/full/';
let pyodide=null,ready=false,busy=false;
async function init(){
  if(ready||busy)return;
  busy=true;
  try{
    importScripts(PYODIDE+'pyodide.js');
    pyodide=await loadPyodide({indexURL:PYODIDE});
    await pyodide.loadPackage('numpy');
    const url=new URL('../../runtime/manta/programmable_matter.py',self.location.href);
    const source=await (await fetch(url,{cache:'no-store'})).text();
    pyodide.FS.writeFile('/home/pyodide/programmable_matter.py',source);
    await pyodide.runPythonAsync("import sys;sys.path.insert(0,'/home/pyodide');from programmable_matter import MantaEngine;manta_engine=MantaEngine(seed=470125)");
    ready=true;
    postMessage({type:'ready',runtime:'python/pyodide',nodes:125});
  }catch(error){
    postMessage({type:'error',error:String(error?.message||error)});
  }finally{busy=false;}
}
self.onmessage=async({data})=>{
  if(data?.type==='init'){await init();return;}
  if(data?.type!=='step'||!ready||busy)return;
  busy=true;
  try{
    pyodide.globals.set('pilot_json',JSON.stringify(data.pilot||{}));
    const result=await pyodide.runPythonAsync(`
import json
p=json.loads(pilot_json)
json.dumps(manta_engine.step_packet(
    pitch=p.get("pitch",0.0),
    roll=p.get("roll",0.0),
    yaw=p.get("yaw",0.0),
    morph=p.get("morph",0.0),
    mode=p.get("mode","CRUISE"),
))
`);
    postMessage({type:'frame',state:JSON.parse(result)});
  }catch(error){
    postMessage({type:'error',error:String(error?.message||error)});
  }finally{busy=false;}
};
