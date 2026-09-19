export const FAILURE_SCHEMA='CITY-INSTRUMENT-FAILURE/1.0';

export function failureTelemetry({componentId,version,phase,error,recoverable=false,context={}}){
  return {
    schema:FAILURE_SCHEMA,
    component_id:componentId,
    version,
    phase,
    error_type:error?.name||'Error',
    message:String(error?.message||error||'unknown failure'),
    recoverable:Boolean(recoverable),
    context,
    timestamp_utc:new Date().toISOString()
  };
}

export function installInstrumentTelemetry({componentId,version}){
  const report=(phase,error,context={})=>{
    const record=failureTelemetry({componentId,version,phase,error,context});
    console.error('[CITY-INSTRUMENT-FAILURE]',record);
    globalThis.dispatchEvent?.(new CustomEvent('city:instrument-failure',{detail:record}));
    return record;
  };
  globalThis.addEventListener?.('error',event=>report('window.error',event.error||new Error(event.message),{
    filename:event.filename||null,lineno:event.lineno||null,colno:event.colno||null
  }));
  globalThis.addEventListener?.('unhandledrejection',event=>report('unhandledrejection',
    event.reason instanceof Error?event.reason:new Error(String(event.reason))));
  globalThis.CITY_INSTRUMENT_TELEMETRY={componentId,version,reportFailure:report};
  return globalThis.CITY_INSTRUMENT_TELEMETRY;
}
