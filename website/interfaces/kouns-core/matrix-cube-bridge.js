/**
 * THE MATRIX -> E47/Cube witness bridge.
 *
 * MATRIX must post:
 *   window.parent.postMessage({
 *     type: "CITY_MATRIX_STATE",
 *     statevector: [[re,im], ... 125 amplitudes],
 *     circuit: { ... optional serializable circuit description ... }
 *   }, "*");
 *
 * This bridge does not claim a 2^n qubit state is automatically the 125-state
 * E47 carrier. The source must explicitly emit the canonical 125-amplitude
 * spin-2 tensor-cube basis.
 */
const ADAPTER="https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter";

export function createMatrixCubeBridge({viewer,onWitness=()=>{}}={}){
  const handler=async event=>{
    if(event.source!==viewer?.contentWindow)return;
    const m=event.data;
    if(!m||m.type!=="CITY_MATRIX_STATE")return;
    try{
      const r=await fetch(ADAPTER,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({statevector:m.statevector,circuit:m.circuit??null})});
      const x=await r.json();
      if(!r.ok||!x.ok)throw new Error(x.error||("adapter "+r.status));
      onWitness(x.witness);
      window.dispatchEvent(new CustomEvent("city:matrix-cube-witness",{detail:x.witness}));
    }catch(error){
      onWitness({error:error instanceof Error?error.message:String(error)});
    }
  };
  addEventListener("message",handler);
  return()=>removeEventListener("message",handler);
}
