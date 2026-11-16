// SKYRMION RT3 · vehicle data.
// Masses, geometry and gear are public-reference figures; aerodynamic coefficients
// are reduced simulation values, not manufacturer data.
const strut=(id,x,y,z,o={})=>({id,x,y,z,radius:.33,travel:.36,springNpm:5.2e5,damperNspm:4.4e4,
 muRoll:.025,muBrake:.42,muSide:.85,braked:true,steerable:false,...o});

const conventional=(id,name,c)=>Object.freeze({id,name,evidence:'conventional',model:'aerodynamic-6dof',
 spool:{idle:.07,spoolUp:2.6,spoolDown:1.4},steerLimitRad:.52,...c});
const experimental=(id,name,c)=>Object.freeze({id,name,evidence:'experimental-simulation',model:'e47-adapter',
 fuelCapacityKg:0,gear:[],...c});

export const VEHICLES=Object.freeze({
 f16:conventional('f16','F-16',{
  dryMassKg:9000,fuelCapacityKg:3200,dryInertia:[12875,75674,85552],
  wing:{area:27.87,span:9.96,chord:3.45},
  aero:{CL0:.18,CLa:4.6,CLde:.72,CLflap:.85,CD0:.022,k:.085,machCrit:.86,waveDragPeak:.026,
   CDflap:.055,CDbrake:.10,CDgear:.025,Cm0:.02,Cma:-.62,Cmq:-8.4,CmDe:-1.05,Cmflap:.05,
   Clp:-.42,ClDa:.13,ClBeta:-.09,Cnr:-.28,CnDr:.17,CnBeta:.12,CyBeta:-.72,CyDr:.21},
  propulsion:'f100',limits:{alpha:.52,beta:.35,g:9},
  fcs:{rollGain:.82,pitchGain:.78,yawGain:.42,rollDamp:.18,pitchDamp:.22,yawDamp:.72,betaDamp:1.35,
   coordination:.035,rollRate:2.8,pitchRate:2.2,yawRate:1.35,throttleRate:1.6,tau:.055,gLimit:9,alphaLimit:.44},
  gear:[strut('nose',3.4,0,2.05,{radius:.28,springNpm:3.1e5,braked:false,steerable:true}),
   strut('left',-.7,-1.25,2.1),strut('right',-.7,1.25,2.1)],
  vRotateMps:72,serviceCeilingM:15240}),

 sr71:conventional('sr71','SR-71',{
  dryMassKg:30600,fuelCapacityKg:46000,dryInertia:[420000,3100000,3250000],
  wing:{area:167,span:16.94,chord:10.8},
  // Slender, area-ruled: a high critical Mach and a shallow drag rise are the whole
  // design intent of the airframe.
  aero:{CL0:.12,CLa:2.65,CLde:.46,CLflap:.35,CD0:.0165,k:.062,machCrit:.95,waveDragPeak:.016,
   CDflap:.03,CDbrake:.07,CDgear:.02,Cm0:.01,Cma:-.38,Cmq:-6.2,CmDe:-.52,Cmflap:.02,
   Clp:-.22,ClDa:.07,ClBeta:-.05,Cnr:-.20,CnDr:.09,CnBeta:.08,CyBeta:-.45,CyDr:.12},
  propulsion:'j58',limits:{alpha:.30,beta:.20,g:3.5},
  fcs:{rollGain:.62,pitchGain:.58,yawGain:.26,rollDamp:.26,pitchDamp:.30,yawDamp:1.05,betaDamp:1.55,
   coordination:.020,rollRate:1.55,pitchRate:1.25,yawRate:.72,throttleRate:.9,tau:.09,gLimit:3.5,alphaLimit:.26},
  gear:[strut('nose',9.2,0,2.6,{radius:.4,springNpm:7.5e5,damperNspm:9e4,braked:false,steerable:true}),
   strut('left',-1.4,-2.4,2.7,{radius:.46,springNpm:1.5e6,damperNspm:1.6e5,travel:.42}),
   strut('right',-1.4,2.4,2.7,{radius:.46,springNpm:1.5e6,damperNspm:1.6e5,travel:.42})],
  vRotateMps:103,serviceCeilingM:25900}),

 x15:conventional('x15','X-15',{
  dryMassKg:6620,fuelCapacityKg:8340,dryInertia:[38000,210000,225000],
  wing:{area:18.6,span:6.8,chord:3.2},
  aero:{CL0:.05,CLa:2.2,CLde:.5,CLflap:.3,CD0:.028,k:.12,machCrit:.90,waveDragPeak:.034,
   CDflap:.04,CDbrake:.12,CDgear:.03,Cm0:0,Cma:-.3,Cmq:-5.4,CmDe:-.65,Cmflap:.03,
   Clp:-.30,ClDa:.08,ClBeta:-.06,Cnr:-.16,CnDr:.10,CnBeta:.09,CyBeta:-.38,CyDr:.13},
  propulsion:'x15_rocket',limits:{alpha:.62,beta:.40,g:7},
  // A rocket motor has no idling turbine: it throttles to zero and responds fast.
  spool:{idle:0,spoolUp:.35,spoolDown:.25},
  fcs:{rollGain:.72,pitchGain:.68,yawGain:.32,rollDamp:.22,pitchDamp:.26,yawDamp:.88,betaDamp:1.20,
   coordination:.018,rollRate:2.0,pitchRate:1.7,yawRate:.95,throttleRate:2.2,tau:.07,gLimit:7,alphaLimit:.5},
  // Skids aft, nose wheel forward: the X-15 lands on steel skids, so side friction
  // is high and there is no wheel braking.
  gear:[strut('nose',4.6,0,1.8,{radius:.26,springNpm:2.6e5,braked:false,steerable:true}),
   strut('left-skid',-3.2,-1.1,1.95,{radius:.12,travel:.22,muRoll:.32,muBrake:.32,muSide:1.1,braked:false}),
   strut('right-skid',-3.2,1.1,1.95,{radius:.12,travel:.22,muRoll:.32,muBrake:.32,muSide:1.1,braked:false})],
  vRotateMps:95,serviceCeilingM:80000}),

 eidolon:experimental('eidolon','EIDOLON',{dryMassKg:9000,dryInertia:[18000,26000,33000],drive:'eidolon_scalar'}),
 manta:experimental('manta','MANTA',{dryMassKg:7200,dryInertia:[15000,23000,26000],drive:'manta_morph'}),
 skyrmion:experimental('skyrmion','SKYRMION',{dryMassKg:8400,dryInertia:[17000,25000,30000],drive:'skyrmion_coherence'}),
 jacob:experimental('jacob','SYNTAX JACOB',{dryMassKg:11000,dryInertia:[25000,36000,41000],drive:'syntax_jacob'})
});
export const VEHICLE_ORDER=['f16','sr71','x15','eidolon','manta','skyrmion','jacob'];
export const vehicle=id=>VEHICLES[id]||VEHICLES.f16;
