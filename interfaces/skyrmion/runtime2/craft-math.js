import {VEHICLES} from './vehicle-registry.js';
import {ENGINES} from './conventional-model.js';
import {EXPERIMENTS} from './experimental-model.js';

const common=[
 ['Translation','dvᵦ/dt = Fᵦ/m + gᵦ − ω × vᵦ'],
 ['Rotation','dω/dt = I⁻¹(τ − ω × Iω)'],
 ['Attitude','dq/dt = ½q ⊗ (0, ω) · RK4 at 120 Hz']
];
const thrustMath={
 f100:'T = 129000 uₜ · clamp(1 − 0.035 max(0, M−1), 0.72, 1.08)',
 j58:'T = 290000 uₜ · clamp(0.58 + 0.22M, 0.55, 1.38)',
 x15_rocket:'T = 254000 uₜ · clamp(1 + 0.12(1−ρ/1.225), 1, 1.13)'
};
export function craftMath(id){
 const v=VEHICLES[id];if(!v)throw new Error('Unknown craft '+id);
 const parameters=[['Mass',`${v.massKg.toLocaleString()} kg`],['Inertia',v.inertia.join(' / ')+' kg·m²']];
 if(v.evidence==='conventional'){
  const a=v.aero;
  return {id,name:v.name,kind:'Conventional aerodynamics',summary:'Independent aerodynamic solver · trimmed launch · engine thrust',parameters:[...parameters,['Wing',`S ${v.wing.area} m² · b ${v.wing.span} m · c ${v.wing.chord} m`],['Engine',`${v.propulsion} · ${ENGINES[v.propulsion].maxThrustN.toLocaleString()} N reference`]],equations:[
   ['Airflow','q̄ = ½ρV² · α = atan2(w,u) · β = asin(v/V)'],
   ['Lift',`L = q̄S Cᴸ · Cᴸ = (${a.CL0} + ${a.CLa} α̃ + 0.72uₚ) max(0,cos α)²`],
   ['Drag',`D = q̄S Cᴰ · Cᴰ = ${a.CD0} + ${a.k} Cᴸ² + 0.04β² + 1.2sin²α`],
   ['Pitch',`Cₘ = ${a.Cm0} + (${a.Cma})α̃ − (${a.CmDe})uₚ − 8ωᵧc/(2V)`],
   ['Pitch feedback',`uₚ,target = uₚ,trim + ${v.fcs.pitchGain} A uₚ,pilot − ${v.fcs.pitchDamp} ωᵧ`],
   ['Thrust',thrustMath[v.propulsion]],...common
  ],note:`Reduced simulation coefficients. α̃ is limited to ±${v.limits.alpha} rad; A is dynamic-pressure control scaling. Positive pilot pitch is nose-up (δₑ = −uₚ). Trim balances lift, thrust, weight and pitch moment.`,sources:[['Flight equations','./runtime2/conventional-model.js'],['Aircraft coefficients','./runtime2/vehicle-registry.js'],['Rigid-body integrator','./runtime2/physics-6dof.js']]};
 }
 const a=EXPERIMENTS[v.propulsion];
 const extra=v.id==='manta'?[
  ['Morph activation','aᵢ = |ψᵢ| / maxⱼ|ψⱼ| · 125 control nodes'],
  ['Morph displacement','Δyᵢ = 0.45(aᵢ−½)Ω + 0.15uₚzᵢ + 0.12uᵣxᵢ'],
  ['Geometry smoothing','rᵢ ← 0.88rᵢ + 0.12 mean(neighbors)']
 ]:[];
 return {id,name:v.name,kind:'Experimental simulation',summary:a.label+' · independent E47 state',parameters:[...parameters,['Thrust scale',a.maxThrustN.toLocaleString()+' N'],['Torque gain',String(a.torqueGain)]],equations:[
  ['Kernel','K = (C−6I)(C−30I) · dim ker K = 47 / 125'],
  ['Spectral step','ψ ← normalize[(I−K²/99144)(ψ+η)]'],
  ['Capture / residual','Ω = ‖P₄₇ψ‖²/‖ψ‖² · r = ‖Kψ‖/‖ψ‖'],
  ['Simulation gain','χ = clamp(0.3 + 0.9Ω − 0.05log₁₀(1+r), 0.15, 1.2)'],
  ['Thrust',`F = ${a.maxThrustN} uₜχ · Fᵦ = (F, 0, −0.04Fuₚ)`],
  ['Torque',`τ = ${a.torqueGain}m(uᵣ, 1.2uₚ, 0.7uᵧ) − 1.8Iω`],
  ...extra,...common
 ],note:'The thrust/torque mapping is a simulation assumption; gravity remains active. η is the runtime input drive. χ is a thrust multiplier, not a probability. '+(v.id==='manta'?'The separate Python worker drives visual geometry; it does not supply measured aerodynamic forces.':v.id==='jacob'?'This flight adapter uses the local coherence model; JPL ephemeris is not part of its force law.':'This craft uses the scalar adapter shown here.'),sources:[['Experimental force law','./runtime2/experimental-model.js'],['E47 spectral runtime','./runtime2/e47-runtime.js'],...(v.id==='manta'?[['MANTA geometry algorithm','../../runtime/manta/programmable_matter.py']]:[])]};
}
export function showCraftMath(id,host){
 if(!host)return;const m=craftMath(id);host.replaceChildren();host.dataset.vehicle=id;
 const heading=document.createElement('h2');heading.textContent=m.name+' · Math';host.appendChild(heading);
 const badge=document.createElement('p');badge.className='math-kind';badge.textContent=m.kind;host.appendChild(badge);
 const summary=document.createElement('p');summary.textContent=m.summary;host.appendChild(summary);
 const params=document.createElement('dl');for(const [key,value] of m.parameters){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=value;params.append(dt,dd);}host.appendChild(params);
 for(const [label,equation] of m.equations){const row=document.createElement('p'),b=document.createElement('strong'),code=document.createElement('code');b.textContent=label;code.textContent=equation;row.append(b,code);host.appendChild(row);}
 const note=document.createElement('p');note.className='math-note';note.textContent=m.note;host.appendChild(note);
 for(const [label,href] of m.sources){const link=document.createElement('a');link.href=href;link.textContent=label;link.target='_blank';link.rel='noopener';host.appendChild(link);}
}
