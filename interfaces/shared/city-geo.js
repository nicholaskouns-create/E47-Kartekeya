// CITY-GEO-1.0
// Shared WGS84 coordinate transform for City simulators.
const R=6378137;
export function metersToWgs84(origin,eastM,northM,upM=0){
  const lat0=origin.lat*Math.PI/180;
  const lat=origin.lat+(northM/R)*180/Math.PI;
  const lon=origin.lon+(eastM/(R*Math.max(.000001,Math.cos(lat0))))*180/Math.PI;
  return {lat,lon,altitude_m:(origin.altitude_m||0)+upM};
}
export function wgs84ToMeters(origin,lat,lon,altitude_m=0){
  const lat0=origin.lat*Math.PI/180;
  return {
    east_m:(lon-origin.lon)*Math.PI/180*R*Math.cos(lat0),
    north_m:(lat-origin.lat)*Math.PI/180*R,
    up_m:altitude_m-(origin.altitude_m||0)
  };
}
export function formatGps(p){
  const ns=p.lat>=0?'N':'S',ew=p.lon>=0?'E':'W';
  return Math.abs(p.lat).toFixed(6)+'° '+ns+' · '+Math.abs(p.lon).toFixed(6)+'° '+ew+' · '+Math.round(p.altitude_m||0)+' m';
}
export const CITY_GEO={
  schema:'CITY-GEO-1.0',
  crs:'EPSG:4326',
  datum:'WGS84',
  defaultOrigin:{lat:36.1699,lon:-115.1398,altitude_m:610,label:'Las Vegas'},
  supabaseTable:'public.city_geo_anchors',
  invariant:'Simulator-local coordinates are mapped to WGS84 for navigation/display only; scientific evidence class is unchanged.'
};
