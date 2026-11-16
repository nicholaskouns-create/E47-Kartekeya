import {clamp} from './math.js';
// WGS84 defining and derived parameters (NIMA TR8350.2) alongside the ISA constants.
// A is the semi-major axis, F the flattening, E2 the first eccentricity squared,
// M_RATIO the ratio of centrifugal to equatorial gravitational acceleration.
const A=6378137, F=1/298.257223563, E2=F*(2-F), M_RATIO=.00344978650684;
const GAMMA_E=9.7803253359, K_SOM=.00193185265241;
const G0=9.80665, T0=288.15, P0=101325, LAPSE=.0065, R_AIR=287.05287, GAMMA=1.4;
export class WorldEngine{
  constructor({wind=[0,0,0]}={}){this.wind=wind;this.schema='SKYRMION-WORLD-ENGINE-2.1'}
  atmosphere(altitudeM){
    const h=clamp(altitudeM,-500,86000);let T,P;
    if(h<=11000){T=T0-LAPSE*h;P=P0*Math.pow(T/T0,G0/(R_AIR*LAPSE));}
    else{T=216.65;const p11=P0*Math.pow(T/T0,G0/(R_AIR*LAPSE));P=p11*Math.exp(-G0*(h-11000)/(R_AIR*T));}
    const rho=P/(R_AIR*T),a=Math.sqrt(GAMMA*R_AIR*T);
    return {temperatureK:T,pressurePa:P,density:rho,speedOfSound:a};
  }
  // Somigliana normal gravity on the WGS84 ellipsoid with the second-order free-air
  // reduction to altitude. Gravity varies with latitude as well as height; a single
  // sphere radius cannot express that and reads about 0.05% low at mid latitudes.
  gravity(altitudeM,latDeg=0){
    const h=Math.max(-500,altitudeM),s=Math.sin(latDeg*Math.PI/180),s2=s*s;
    const g0=GAMMA_E*(1+K_SOM*s2)/Math.sqrt(1-E2*s2);
    return g0*(1-2*h/A*(1+F+M_RATIO-2*F*s2)+3*h*h/(A*A));
  }
  sample(state){const atm=this.atmosphere(state.position.altitudeM);return {...atm,gravity:this.gravity(state.position.altitudeM,state.position.lat),windNed:[...this.wind]};}
  // Geodetic integration on the WGS84 ellipsoid. The meridian radius of curvature M
  // and the prime-vertical radius N differ by up to 0.7%, so north-south and
  // east-west ground rates are carried separately rather than by one sphere radius.
  integrateGeodetic(position,velocityNed,dt){
    const lat=position.lat*Math.PI/180,alt=position.altitudeM;
    const s=Math.sin(lat),w=Math.sqrt(1-E2*s*s);
    const M=A*(1-E2)/(w*w*w),N=A/w;
    const dLat=velocityNed[0]/(M+alt),dLon=velocityNed[1]/((N+alt)*Math.max(1e-6,Math.cos(lat))),dAlt=-velocityNed[2];
    return {lat:position.lat+dLat*dt*180/Math.PI,lon:position.lon+dLon*dt*180/Math.PI,altitudeM:Math.max(-200,alt+dAlt*dt)};
  }
}
