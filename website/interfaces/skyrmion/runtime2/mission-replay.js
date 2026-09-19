export class MissionReplay{
 constructor({hz=10,maxSeconds=1800}={}){this.hz=hz;this.max=Math.max(10,hz*maxSeconds);this.frames=[];this.acc=0;this.recording=true;this.replaying=false;this.schema='SKYRMION-MISSION-2.0';this._raf=0;}
 sample(state,telemetry,dt){if(!this.recording||this.replaying)return;this.acc+=dt;if(this.acc<1/this.hz)return;this.acc=0;const frame={t:state.t,vehicleId:state.vehicleId,position:{...state.position},velocityBody:[...state.velocityBody],quaternion:[...state.quaternion],omegaBody:[...state.omegaBody],controls:{...state.controls},telemetry};this.frames.push(frame);if(this.frames.length>this.max)this.frames.shift();}
 clear(){this.stopReplay();this.frames.length=0}
 export(){return {schema:this.schema,createdAt:new Date().toISOString(),hz:this.hz,frames:this.frames}}
 startReplay(apply,{speed=1,loop=false}={}){if(this.frames.length<2)return false;this.stopReplay();this.replaying=true;this.recording=false;let i=0,last=performance.now(),carry=0;const interval=1000/(this.hz*Math.max(.1,speed));const tick=now=>{if(!this.replaying)return;carry+=now-last;last=now;while(carry>=interval&&this.replaying){carry-=interval;apply(this.frames[i]);i++;if(i>=this.frames.length){if(loop)i=0;else{this.stopReplay();return;}}}this._raf=requestAnimationFrame(tick)};this._raf=requestAnimationFrame(tick);return true;}
 stopReplay(){this.replaying=false;if(this._raf)cancelAnimationFrame(this._raf);this._raf=0;this.recording=true;}
}
