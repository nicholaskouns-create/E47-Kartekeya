import {installFlightInteractionStandard} from '../shared/flight-interaction-standard.js';
import {MantaABRuntime,missionCommand,DT,MISSION_DURATION_S} from './manta-model.js';

let latest=null;
const originalStep=MantaABRuntime.prototype.step;
if(!MantaABRuntime.prototype.__cityFlight24){
  MantaABRuntime.prototype.__cityFlight24=true;
  MantaABRuntime.prototype.step=function(){
    if(this.done)return this.snapshot();
    const scripted=missionCommand(this.t);
    const c=latest;
    const cmd=c?.engaged?{
      ...scripted,
      throttle:c.throttle,
      roll:c.roll*.18,
      pitch:c.pitch*.12,
      yaw:c.yaw*.12,
      phase:'PILOT'
    }:scripted;
    this.stepCase(this.morphCase,cmd);this.stepCase(this.baseCase,cmd);
    this.t+=DT;this.frame++;
    if(this.t>=MISSION_DURATION_S)this.done=true;
    return this.snapshot(cmd.phase);
  };
}

const flight=installFlightInteractionStandard({
  surface:'MANTA',
  baseThrottle:.76,
  cameraModes:['CHASE','WING','ORBIT'],
  mountHud:true,
  onControls:d=>{latest=d},
  onCamera:()=>document.getElementById('view')?.click()
});
window.CITY_MANTA_FLIGHT_INPUT=flight;
window.addEventListener('beforeunload',()=>{if(MantaABRuntime.prototype.__cityFlight24)MantaABRuntime.prototype.step=originalStep},{once:true});
