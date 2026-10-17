import{makeCity125,applyPacket,markE47,browserWitness}from'./city-125-runtime.js';
export const CONTRACT='MATRIX-CITY125-E47-AETHERIS-1.0';
const abs2=z=>z[0]*z[0]+z[1]*z[1];
export function instantiateMatrixCityAdapter({emitReceipt=async p=>({schema:'AETHERIS-RECEIPT-1.0',status:'local-witness',packet:p})}={}){
 let cells=makeCity125(),sequence=0;
 return {get cells(){return cells},async ingest({statevector,circuit,e47Witness}){
  if(!Array.isArray(statevector)||statevector.length!==125)throw Error('typed lift must contain exactly 125 complex amplitudes');
  const weights=statevector.map(abs2),sum=weights.reduce((a,b)=>a+b,0);if(!(sum>0))throw Error('zero 125-vector');
  const packet={object:{type:'MATRIX_FEATURE_125',contract:CONTRACT,circuit},operator:{matrix:'two-site-mps→explicit-feature-lift',e47:'P47/K spectral witness',cube:'address fabric only'},invariant:{dimension:125,representation_separation:true,human_promotion_gate:true},witness:{sequence:++sequence,e47:e47Witness??null,amplitude_weights:weights.map(x=>x/sum)},evidence:'E2-simulation-with-E1-software-checks',provenance:{source:'THE MATRIX',lift:circuit?.lift??null,adapter:CONTRACT},next_action:'aetheris',addresses:Array.from({length:125},(_,i)=>i)};
  applyPacket(cells,packet);
  if(e47Witness?.projected_weights?.length===125)cells=markE47(cells,e47Witness.projected_weights);
  const receipt=await emitReceipt(packet);for(const c of cells)c.receipt=receipt;
  return {packet,receipt,city:browserWitness(cells),cells};
 }};
}
