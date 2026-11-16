// SKYRMION RT3 · US Standard Atmosphere 1976 to 86 km, plus wind and turbulence.
import {clamp} from './math.js';
const G0=9.80665, R_AIR=287.05287, GAMMA=1.4, S_SUTH=110.4, MU0=1.716e-5, T_REF=273.15;
// Geopotential base altitude, lapse rate, base temperature, base pressure per layer.
const LAYERS=[
 {h:0,      L:-.0065, T:288.15, P:101325},
 {h:11000,  L:0,      T:216.65, P:22632.06},
 {h:20000,  L:.001,   T:216.65, P:5474.889},
 {h:32000,  L:.0028,  T:228.65, P:868.0187},
 {h:47000,  L:0,      T:270.65, P:110.9063},
 {h:51000,  L:-.0028, T:270.65, P:66.93887},
 {h:71000,  L:-.002,  T:214.65, P:3.956420}
];
const RE=6356766; // Earth radius used by the 1976 geopotential definition.
export const geopotential=z=>RE*z/(RE+z);

export function standardAtmosphere(altitudeM){
 const h=geopotential(clamp(altitudeM,-5000,86000));
 let i=0;while(i<LAYERS.length-1&&h>=LAYERS[i+1].h)i++;
 const b=LAYERS[i],dh=h-b.h;
 const T=b.T+b.L*dh;
 const P=b.L===0?b.P*Math.exp(-G0*dh/(R_AIR*b.T)):b.P*Math.pow(T/b.T,-G0/(R_AIR*b.L));
 const density=P/(R_AIR*T);
 return {
  temperatureK:T,pressurePa:P,density,
  speedOfSound:Math.sqrt(GAMMA*R_AIR*T),
  // Sutherland's law: viscosity is needed for Reynolds number, which sets skin friction.
  viscosity:MU0*Math.pow(T/T_REF,1.5)*(T_REF+S_SUTH)/(T+S_SUTH)
 };
}
// Logarithmic boundary-layer wind profile over a roughness length, veering with
// height toward the geostrophic direction.
export function windProfile({speed10=0,direction10=0,altitudeAglM=0,roughness=.1}={}){
 const z=Math.max(roughness*1.5,altitudeAglM);
 const factor=Math.log(z/roughness)/Math.log(10/roughness);
 const veer=clamp(altitudeAglM/900,0,1)*25*Math.PI/180;
 const speed=speed10*clamp(factor,0,3.2),dir=direction10+veer;
 return [-speed*Math.cos(dir),-speed*Math.sin(dir),0];
}
// Dryden continuous-gust model (MIL-F-8785C), discrete-time first-order form.
// Turbulence is what makes a simulator feel like air rather than like a spreadsheet.
export class DrydenTurbulence{
 constructor({intensity=1,seed=47}={}){
  this.schema='RT3-DRYDEN-1.0';this.intensity=intensity;this.state=[0,0,0];
  let x=(seed|0)||1;
  this.rand=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;const u=((x>>>0)%1000000+1)/1000001;
   x^=x<<13;x^=x>>>17;x^=x<<5;const v=((x>>>0)%1000000+1)/1000001;
   return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)};
 }
 // Scale lengths and sigmas follow the low-altitude MIL spec below 1000 ft and
 // relax to the 1750 ft high-altitude scale above it.
 scales(altitudeAglM,windSpeed10){
  const ft=Math.max(3,altitudeAglM*3.28084);
  if(ft<1000){
   const Lw=ft,Lu=ft/Math.pow(.177+.000823*ft,1.2);
   const sw=.1*windSpeed10,su=sw/Math.pow(.177+.000823*ft,.4);
   return {Lu,Lv:Lu,Lw,su,sv:su,sw};
  }
  const L=533.4,s=.1*windSpeed10*clamp(1-(ft-1000)/20000,.25,1);
  return {Lu:L,Lv:L,Lw:L,su:s,sv:s,sw:s};
 }
 step(dt,trueAirspeed,altitudeAglM,windSpeed10=6){
  const V=Math.max(12,trueAirspeed),{Lu,Lv,Lw,su,sv,sw}=this.scales(altitudeAglM,windSpeed10);
  const L=[Lu,Lv,Lw],S=[su,sv,sw];
  for(let i=0;i<3;i++){
   const tau=L[i]/V,beta=Math.exp(-dt/tau);
   const sigma=S[i]*this.intensity*Math.sqrt(1-beta*beta);
   this.state[i]=beta*this.state[i]+sigma*this.rand();
  }
  return [...this.state];
 }
 reset(){this.state=[0,0,0];return this}
}
