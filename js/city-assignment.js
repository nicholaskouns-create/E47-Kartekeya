/* Canonical read-only City assignment consumer.
   Use this same script in Citadel, Citizenship Bureau, Proof Forge and publication pages.
   Never infer an evidence grade from presentation, URL or service-specific state. */
(async function(){
  const mount=document.querySelector("[data-city-assignment]");
  if(!mount)return;
  const source=mount.getAttribute("data-source")||"/E47-Kartekeya/data/city-assignment.json";
  try{
    const res=await fetch(source,{cache:"no-store"});
    if(!res.ok)throw new Error("HTTP "+res.status);
    const record=await res.json();
    if(record.schema!=="MC-CIVIC-ASSIGNMENT/2.0"||!Array.isArray(record.claims)||record.claim_count!==record.claims.length||!record.assignment_sha256)throw new Error("invalid schema");
    const surface=mount.getAttribute("data-surface")||"publication";
    if(!record.surfaces[surface]||record.surfaces[surface].assignment_sha256!==record.assignment_sha256)throw new Error("surface digest mismatch");
    const heading=document.createElement("h3");
    heading.textContent="Canonical civic assignment · "+surface.replaceAll("_"," ");
    const detail=document.createElement("p");
    detail.textContent=record.claim_count+" validated claims · "+record.assignment_sha256.slice(0,16)+"… · source: "+record.source;
    const list=document.createElement("ul");
    for(const claim of record.claims){
      const li=document.createElement("li");
      li.textContent=claim.id+" · "+claim.evidence+" · "+claim.civic_state+(claim.conditional_on.length?" · conditional":"");
      list.append(li);
    }
    mount.replaceChildren(heading,detail,list);
    mount.dataset.assignmentHash=record.assignment_sha256;
  }catch(e){
    mount.textContent="ASSIGNMENT UNAVAILABLE · fail closed; no evidence status asserted ("+e.message+")";
    mount.dataset.status="unavailable";
  }
})();