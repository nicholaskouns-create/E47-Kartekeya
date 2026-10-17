export const CITY_FIELDS=["object","operator","invariant","witness","evidence","provenance","next_action"];
export const idx=(x,y,z)=>25*x+5*y+z;
export const xyz=i=>[Math.floor(i/25),Math.floor(i/5)%5,i%5];
export function makeCity125(){
 return Array.from({length:125},(_,i)=>({i,xyz:xyz(i),source:null,state:null,operator:null,evidence:null,receipt:null,provenance:[],e47:false,updated_at:null}));
}
export function applyPacket(cells,packet){
 for(const k of CITY_FIELDS) if(!(k in packet)) throw Error("CITY-INVARIANT missing "+k);
 const targets=packet.addresses??Array.from({length:125},(_,i)=>i);
 const now=new Date().toISOString();
 for(const i of targets){if(i<0||i>=125)throw Error("address out of range");let c=cells[i];c.source=packet.object;c.state=packet.witness;c.operator=packet.operator;c.evidence=packet.evidence;c.receipt=packet.receipt??null;c.provenance=[...c.provenance,packet.provenance];c.updated_at=now;}
 return cells;
}
export function applyPermutation(cells,perm){
 if(perm.length!==125||new Set(perm).size!==125)throw Error("not a 125 permutation");
 const out=Array(125);for(let i=0;i<125;i++)out[perm[i]]={...cells[i],i:perm[i],xyz:xyz(perm[i])};return out;
}
export function markE47(cells,weights,threshold=1e-12){
 if(weights.length!==125)throw Error("E47 weight vector must have 125 entries");
 return cells.map((c,i)=>({...c,e47:weights[i]>threshold}));
}
export function route(packet,routes){
 const n=packet.next_action;if(!n)return null;return routes.find(r=>r.accepts.includes(n)||r.id===n)??null;
}
export function browserWitness(cells){
 return {carrier:cells.length,base5:cells.length===5**3,evidence:new Set(cells.map(c=>c.evidence).filter(Boolean)).size,receipts:cells.filter(c=>c.receipt).length,e47_cells:cells.filter(c=>c.e47).length};
}