import sys,json,subprocess,warnings,os
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[2])
from datetime import datetime,timezone,timedelta
sys.path.insert(0,'apps/gaze')
from app import calculate,separation
cases=[]
with warnings.catch_warnings():
 warnings.simplefilter('ignore')
 for lat,lon,h in [(36.1716,-115.1391,610),(-33.86,151.21,0)]:
  for days in [-24,0,24]:
   dt=datetime(2026,9,29,tzinfo=timezone.utc)+timedelta(days=days)
   cases.append(dict(date=dt.isoformat(),lat=lat,lon=lon,height=h,python=calculate(dt,lat,lon,h)))
js="""const A=require('./website/interfaces/gaze/vendor/astronomy.browser.min.js');require('./website/interfaces/gaze/sky.js');const cases=JSON.parse(process.argv[1]);console.log(JSON.stringify(cases.map(c=>GazeSky.calculate(A,new Date(c.date),c.lat,c.lon,c.height))));"""
web=json.loads(subprocess.check_output(['node','-e',js,json.dumps(cases)]))
res=[]
for c,rows in zip(cases,web):
 for r in rows:
  p=c['python'][r['name']];err=separation(p,r);res.append(err)
  assert err<0.1,(c['date'],r['name'],err)
assert separation({'alt':0,'az':359},{'alt':0,'az':1})<2.00001
assert abs(separation({'alt':90,'az':0},{'alt':90,'az':180}))<1e-5
from streamlit.testing.v1 import AppTest
app=AppTest.from_file(str(Path('apps/gaze/app.py').resolve())).run(timeout=60)
assert not app.exception,app.exception
app.slider[0].set_value(12).run(timeout=60)
assert not app.exception,app.exception
app.radio[0].set_value('Days').run(timeout=60)
assert not app.exception,app.exception
result={'status':'PASS','coordinate_comparisons':48,'max_angular_difference_degrees':max(res),'comparison_tolerance_degrees':0.1,'streamlit_runs':['default','12 hours','12 days'],'separation_checks':['azimuth wrap','zenith'],'note':'Implementation comparison, not measured sky validation.'}
print(json.dumps(result,indent=2))
open('apps/gaze/validation.json','w').write(json.dumps(result,indent=2)+'\n')
