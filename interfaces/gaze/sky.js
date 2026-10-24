/* Astronomy Engine 2.1.19; fixed J2000 catalog, no proper-motion propagation. */
(function(root){
'use strict';
const stars=[['Polaris',2+31/60+49.09/3600,89+15/60+50.8/3600],['Vega',18+36/60+56.33/3600,38+47/60+1.2/3600],['Deneb',20+41/60+25.91/3600,45+16/60+49.2/3600],['Sirius',6+45/60+8.92/3600,-(16+42/60+58/3600)]];
function separation(a,b){const r=Math.PI/180,h1=a.alt*r,h2=b.alt*r,d=(a.az-b.az)*r;return Math.acos(Math.max(-1,Math.min(1,Math.sin(h1)*Math.sin(h2)+Math.cos(h1)*Math.cos(h2)*Math.cos(d))))/r;}
function calculate(A,date,lat,lon,height){
 if(!Number.isFinite(+date)||!Number.isFinite(lat)||Math.abs(lat)>90||!Number.isFinite(lon)||Math.abs(lon)>180||!Number.isFinite(height))throw Error('Enter a valid date and finite location (latitude ±90°, longitude ±180°).');
 const observer=new A.Observer(lat,lon,height);
 const targets=stars.map(([name,ra,dec],i)=>{const body='Star'+(i+1);A.DefineStar(body,ra,dec,1e9);return {name,body,type:'Star'};}).concat(['Moon','Jupiter','Saturn','Venus'].map(name=>({name,body:name,type:'Planet/Satellite'})));
 return targets.map(o=>{const eq=A.Equator(o.body,date,observer,true,true),h=A.Horizon(date,observer,eq.ra,eq.dec);return {...o,alt:h.altitude,az:h.azimuth};});
}
root.GazeSky={calculate,separation};
})(typeof globalThis!=='undefined'?globalThis:this);
