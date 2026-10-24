// STARGATE-SIMULATOR-INVARIANTS-1.0
// Shared corrected formalism for Mathematical City simulators.
// This module carries exact/conditional mathematics and evidence boundaries.
// It does not convert simulated coherence, E47 capture, scalar fields, or vehicle state
// into evidence of a physical wormhole or metric-engineering device.

export const STARGATE_FORMALISM=Object.freeze({
  schema:'STARGATE-SIMULATOR-INVARIANTS-1.0',
  validation:'STARGATE-CORRECTED-VALIDATION-1.1',
  certificate:'MC-STARGATE-CORRECTED-20260919',
  evidence:Object.freeze({
    exact:'E0',
    machine:'E1',
    simulator:'E2',
    physicalClosure:'OPEN'
  }),
  constants:Object.freeze({
    omega_c:47/125,
    sech4_integral:4/3,
    c_m_s:299792458,
    planck_time_s:5.391247e-44
  }),
  equations:Object.freeze({
    profile:'rho(l)=Omega_c+epsilon*tanh(l/ell)',
    profileGradient:'d rho/dl=(epsilon/ell)*sech^2(l/ell)',
    profileGradientSquared:'(d rho/dl)^2=(epsilon^2/ell^2)*sech^4(l/ell)',
    radialNEC:'epsilon+p_l=Z(chi)*(d rho/dl)^2',
    throat:'b(r0)=r0; flare-out requires b_prime(r0)<1',
    staticSpectrum:'lambda(k)=m^2+Z*k^2+alpha*k^4',
    staticMinimum:'lambda_min=m^2-Z^2/(4*alpha) for Z<0, alpha>0',
    memoryAverage:'chi_avg=(1/tau)*integral c(t)dt',
    memoryAccumulation:'chi_acc=(1/tau_ref)*integral c(t)dt',
    conservation:'nabla_mu T_total^{mu nu}=0'
  }),
  gates:Object.freeze({
    e47RankFractionIsPhysicalThreshold:false,
    normalizedAverageAutomaticallyAccumulates:false,
    negativeStiffnessAloneIsStable:false,
    staticHessianImpliesLorentzianStability:false,
    localForceDensityEqualsNetThrust:false,
    physicalWormholeValidated:false,
    empiricalNECViolationValidated:false,
    hardwareStargateValidated:false
  }),
  boundary:'Corrected Stargate formalism is a conditional mathematical/simulation layer. Full nonlinear Einstein closure, ghost-free Lorentzian stability, empirical NEC violation, and hardware realization remain open.'
});

const finite=n=>Number.isFinite(Number(n));
const sech=x=>1/Math.cosh(x);
const clean=n=>finite(n)?Number(n):null;

export function evaluateStargateConditional(input={}){
  const l=clean(input.l),epsilon=clean(input.epsilon),ell=clean(input.ell);
  const Z=clean(input.Z),m2=clean(input.m2),alpha=clean(input.alpha);
  const tau=clean(input.tau),tauRef=clean(input.tauRef),coherenceRate=clean(input.coherenceRate);
  const sizeM=clean(input.sizeM),omegaGradient=clean(input.omegaGradient),backgroundStress=clean(input.backgroundStress);

  const profile=(l!==null&&epsilon!==null&&ell!==null&&ell!==0)
    ? STARGATE_FORMALISM.constants.omega_c+epsilon*Math.tanh(l/ell):null;
  const gradient=(l!==null&&epsilon!==null&&ell!==null&&ell!==0)
    ? (epsilon/ell)*sech(l/ell)**2:null;
  const gradientSquared=gradient===null?null:gradient*gradient;
  const radialNEC=(Z!==null&&gradientSquared!==null)?Z*gradientSquared:null;

  let staticHessianMin=null,staticHessianPositive=null;
  if(Z!==null&&m2!==null&&alpha!==null&&alpha>0){
    staticHessianMin=Z<0?m2-(Z*Z)/(4*alpha):m2;
    staticHessianPositive=staticHessianMin>0;
  }

  const chiAverage=(coherenceRate!==null)?coherenceRate:null;
  const chiAccum=(coherenceRate!==null&&tau!==null&&tauRef!==null&&tauRef>0)
    ? coherenceRate*tau/tauRef:null;
  const causalFloorS=(sizeM!==null&&sizeM>=0)
    ? sizeM/STARGATE_FORMALISM.constants.c_m_s:null;
  const couplingDivergence=(omegaGradient!==null&&backgroundStress!==null)
    ? -backgroundStress*omegaGradient:null;

  return Object.freeze({
    profile,gradient,gradientSquared,radialNEC,
    flareOutSupportConditional:radialNEC!==null?radialNEC<0:null,
    staticHessianMin,staticHessianPositive,
    chiAverage,chiAccum,causalFloorS,couplingDivergence
  });
}

export function createStargatePacket({
  surface='unknown',
  modeled={},
  conditional={},
  timestamp=new Date().toISOString()
}={}){
  return Object.freeze({
    schema:'CITY-STARGATE-SIM-PACKET-1.0',
    timestamp,
    surface,
    evidence_class:'E2',
    formalism:STARGATE_FORMALISM,
    modeled_observables:Object.freeze({...modeled}),
    conditional:evaluateStargateConditional(conditional),
    interpretation:Object.freeze({
      modeledObservablesArePhysicalBridge:false,
      physicalPromotion:false,
      note:'Simulator observables are retained as E2 model state unless independently mapped and validated.'
    })
  });
}

export function installStargateInvariantBridge({
  surface='unknown',
  container=null,
  readModeled=()=>({}),
  readConditional=()=>({}),
  postTarget=null,
  intervalMs=1000,
  eventName='city:stargate-invariants'
}={}){
  const host=container||document.querySelector('.hud .top .cluster')||document.querySelector('.status-strip')||document.body;
  const chip=document.createElement('span');
  chip.className='chip stargate-chip';
  chip.textContent='STARGATE · 47/125 · OPEN';
  chip.title=STARGATE_FORMALISM.boundary;
  if(host&&host!==document.body)host.appendChild(chip);

  let packet=createStargatePacket({surface});
  const publish=()=>{
    packet=createStargatePacket({
      surface,
      modeled:readModeled?.()||{},
      conditional:readConditional?.()||{}
    });
    try{window.dispatchEvent(new CustomEvent(eventName,{detail:packet}))}catch{}
    try{window.parent?.postMessage({type:'city.stargate.invariants',packet},'*')}catch{}
    try{postTarget?.contentWindow?.postMessage({type:'city.stargate.invariants',packet},'*')}catch{}
    return packet;
  };
  publish();
  const timer=setInterval(publish,Math.max(250,Number(intervalMs)||1000));
  return Object.freeze({
    formalism:STARGATE_FORMALISM,
    packet:()=>packet,
    publish,
    destroy:()=>clearInterval(timer)
  });
}
