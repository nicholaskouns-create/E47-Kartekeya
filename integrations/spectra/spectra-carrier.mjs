/* SPECTRA common carrier and QASM bridge, no runtime or database credentials. */
export function carrierIndex(x,y,z) {
  if (![x,y,z].every(v=>Number.isInteger(v)&&v>=0&&v<5)) throw new RangeError("Base-5 coordinates must be integers in [0,4]");
  return 25*x+5*y+z;
}
export function carrierCoordinates(i) {
  if (!Number.isInteger(i)||i<0||i>=125) throw new RangeError("Carrier index must be in [0,124]");
  return [Math.floor(i/25),Math.floor(i%25/5),i%5];
}
export function carrierQasm(i,{measure=true}={}) {
  carrierCoordinates(i);
  const s=["OPENQASM 2.0;",'include "qelib1.inc";',"qreg q[7];","creg c[7];"];
  for(let q=0;q<7;q++) if(i&(1<<q)) s.push("x q["+q+"];");
  if(measure) for(let q=0;q<7;q++)s.push("measure q["+q+"] -> c["+q+"];");
  return s.join("\n");
}
export function parseSpectraQasm(source) {
  if(typeof source!=="string"||source.length>100000)throw new Error("Invalid QASM size");
  let hasHeader=false,hasQreg=false;
  const gates=[];
  for(const raw of source.split(/\r?\n/)){
    const line=raw.replace(/\/\/.*$/,"").trim();
    if(!line)continue;
    if(/^OPENQASM\s+2\.0\s*;$/i.test(line)){hasHeader=true;continue;}
    if(/^include\s+"qelib1\.inc"\s*;$/i.test(line)||/^creg\s+c\[7\]\s*;$/i.test(line))continue;
    if(/^qreg\s+q\[7\]\s*;$/i.test(line)){hasQreg=true;continue;}
    let m=line.match(/^(x|h)\s+q\[(\d+)\]\s*;$/i);
    if(m){const q=Number(m[2]);if(q>6)throw new Error("Qubit out of range");gates.push({gate:m[1].toUpperCase(),targets:[q]});continue;}
    m=line.match(/^cx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]\s*;$/i);
    if(m){const a=Number(m[1]),b=Number(m[2]);if(a>6||b>6||a===b)throw new Error("Invalid CNOT");gates.push({gate:"CNOT",targets:[a,b]});continue;}
    m=line.match(/^measure\s+q\[(\d+)\]\s*->\s*c\[(\d+)\]\s*;$/i);
    if(m){const q=Number(m[1]),c=Number(m[2]);if(q>6||c>6)throw new Error("Invalid measurement");gates.push({gate:"MEASURE",targets:[q,c]});continue;}
    throw new Error("Unsupported OpenQASM statement: "+line.slice(0,80));
  }
  if(!hasHeader||!hasQreg||gates.length>5000)throw new Error("Missing QASM header/register or too many gates");
  return gates;
}
export function decodeSpectraCounts(counts){
  let total=0,leakageShots=0;
  const points=Object.entries(counts).map(([bits,shots])=>{
    if(!/^[01]{7}$/.test(bits)||!Number.isSafeInteger(shots)||shots<0)throw new Error("Invalid count");
    const index=parseInt(bits,2);total+=shots;if(index>=125)leakageShots+=shots;
    return {bits,index,shots,leakage:index>=125};
  });
  return {points,total,leakageShots,leakageFraction:total?leakageShots/total:0};
}
