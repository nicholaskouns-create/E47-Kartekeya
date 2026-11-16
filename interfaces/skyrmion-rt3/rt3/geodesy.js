// SKYRMION RT3 · WGS84 geodesy.
// Defining parameters, NIMA TR8350.2. Everything else here is derived from them.
export const WGS84=Object.freeze({
 a:6378137, f:1/298.257223563, GM:3.986004418e14, omega:7.292115e-5
});
export const E2=WGS84.f*(2-WGS84.f);
const GAMMA_E=9.7803253359, K_SOM=.00193185265241, M_RATIO=.00344978650684;
const DEG=Math.PI/180;

// Meridian and prime-vertical radii of curvature. They differ by up to 0.7%, so a
// single sphere radius mis-rates north-south motion against east-west motion.
export function curvature(latRad){
 const s=Math.sin(latRad),w=Math.sqrt(1-E2*s*s);
 return {M:WGS84.a*(1-E2)/(w*w*w),N:WGS84.a/w};
}
// Somigliana normal gravity with the second-order free-air reduction to altitude.
export function normalGravity(altitudeM,latDeg){
 const h=Math.max(-500,altitudeM),s=Math.sin(latDeg*DEG),s2=s*s;
 const g0=GAMMA_E*(1+K_SOM*s2)/Math.sqrt(1-E2*s2);
 return g0*(1-2*h/WGS84.a*(1+WGS84.f+M_RATIO-2*WGS84.f*s2)+3*h*h/(WGS84.a*WGS84.a));
}
// Earth rotation rate resolved in the local NED frame.
export function earthRateNed(latDeg){
 const lat=latDeg*DEG;
 return [WGS84.omega*Math.cos(lat),0,-WGS84.omega*Math.sin(lat)];
}
// Transport rate: the angular velocity of the NED frame itself as the vehicle moves
// over a curved Earth. Omitting it is why long-range sims drift in heading.
export function transportRateNed(position,velocityNed){
 const lat=position.lat*DEG,{M,N}=curvature(lat),h=position.altitudeM;
 const [vN,vE]=velocityNed;
 return [vE/(N+h),-vN/(M+h),-vE*Math.tan(lat)/(N+h)];
}
export function integrateGeodetic(position,velocityNed,dt){
 const lat=position.lat*DEG,{M,N}=curvature(lat),h=position.altitudeM;
 const dLat=velocityNed[0]/(M+h);
 const dLon=velocityNed[1]/((N+h)*Math.max(1e-6,Math.cos(lat)));
 return {
  lat:position.lat+dLat*dt/DEG,
  lon:((position.lon+dLon*dt/DEG+540)%360)-180,
  altitudeM:h-velocityNed[2]*dt
 };
}
export function geodeticToEcef(position){
 const lat=position.lat*DEG,lon=position.lon*DEG,h=position.altitudeM;
 const s=Math.sin(lat),c=Math.cos(lat),{N}=curvature(lat);
 return [(N+h)*c*Math.cos(lon),(N+h)*c*Math.sin(lon),(N*(1-E2)+h)*s];
}
// Great-circle distance on the ellipsoid, mean-radius approximation; used for range
// readouts, not for integration.
export function rangeMeters(a,b){
 const p1=a.lat*DEG,p2=b.lat*DEG,dp=p2-p1,dl=(b.lon-a.lon)*DEG;
 const h=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;
 return 2*6371008.8*Math.asin(Math.min(1,Math.sqrt(h)));
}
