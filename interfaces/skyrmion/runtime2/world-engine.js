import {clamp} from './math.js';
const R=6378137, G0=9.80665, T0=288.15, P0=101325, LAPSE=.0065, R_AIR=287.05287, GAMMA=1.4;
export class WorldEngine{
  constructor({wind=[0,0,0]}={}){this.wind=wind;this.schema='SKYRMION-WORLD-ENGINE-2.0'}
  atmosphere(altitudeM){
    const h=clamp(altitudeM,-500,86000);let T,P;
    if(h<=11000){T=T0-LAPSE*h;P=P0*Math.pow(T/T0,G0/(R_AIR*LAPSE));}
    else{T=216.65;const p11=P0*Math.pow(T/T0,G0/(R_AIR*LAPSE));P=p11*Math.exp(-G0*(h-11000)/(R_AIR*T));}
    const rho=P/(R_AIR*T),a=Math.sqrt(GAMMA*R_AIR*T);
    return {temperatureK:T,pressurePa:P,density:rho,speedOfSound:a};
  }
  gravity(altitudeM){return G0*Math.pow(R/(R+Math.max(-500,altitudeM)),2)}
  sample(state){const atm=this.atmosphere(state.position.altitudeM);return {...atm,gravity:this.gravity(state.position.altitudeM),windNed:[...this.wind]};}
  integrateGeodetic(position,velocityNed,dt){
    const lat=position.lat*Math.PI/180,alt=position.altitudeM;
    const dLat=velocityNed[0]/(R+alt),dLon=velocityNed[1]/((R+alt)*Math.max(1e-6,Math.cos(lat))),dAlt=-velocityNed[2];
    return {lat:position.lat+dLat*dt*180/Math.PI,lon:position.lon+dLon*dt*180/Math.PI,altitudeM:Math.max(-200,alt+dAlt*dt)};
  }
}
