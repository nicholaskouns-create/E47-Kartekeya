"""Behavioral browser QA for the standalone Observatory and additive bridge."""
from pathlib import Path
import json, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'website')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    checks=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            for name,size in [('desktop',{'width':1440,'height':1000}),('mobile',{'width':390,'height':844})]:
                page=browser.new_page(viewport=size)
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                response=page.goto(base+'/interfaces/observatory/')
                assert response.status==200
                page.wait_for_function("window.cityObservatory && document.querySelectorAll('.atlas-card').length > 20")
                assert page.locator('#view-city').is_visible()
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                page.locator('[data-view=signal]').click()
                page.locator('#overlap').fill('0');page.locator('#overlap').dispatch_event('input')
                assert page.locator('#fidelity').inner_text()=='Undefined'
                page.locator('#overlap').fill('1');page.locator('#overlap').dispatch_event('input')
                assert page.locator('#probability').inner_text()=='100.00%'
                assert page.locator('#residual').inner_text()=='0.00e+0'
                page.wait_for_function("document.getElementById('quantum-state').textContent==='READY'")
                page.locator('#quantum-teacher').click()
                assert abs(float(page.locator('#quantum-expectation').inner_text())-.03649278674695777)<1e-5
                assert page.locator('#quantum-norm').inner_text()=='1.00000000'
                page.locator('[data-view=learn]').click()
                initial=page.locator('#loss').inner_text()
                for _ in range(5):page.locator('#train-step').click()
                assert page.locator('#epoch').inner_text()=='100'
                assert float(page.locator('#loss').inner_text())<float(initial)
                before=page.evaluate('window.cityObservatory.getState()')
                text=page.evaluate('window.cityObservatory.exportReplay()')
                page.locator('#train-reset').click()
                page.evaluate('(text)=>window.cityObservatory.importReplay(text)',text)
                assert page.evaluate('window.cityObservatory.getState()')==before
                rejected=page.evaluate("()=>{try{window.cityObservatory.importReplay('{\"schema\":\"wrong\"}');return false}catch{return true}}")
                assert rejected
                page.locator('#rate').fill('0.3');page.locator('#rate').dispatch_event('input')
                assert page.locator('#epoch').inner_text()=='0'
                page.locator('#settings-open').click();page.locator('#reading-setting').check();page.locator('#reduce-motion').check();page.locator('#settings .primary').click()
                assert page.locator('body').evaluate("e=>e.classList.contains('reading') && e.classList.contains('reduced-motion')")
                page.locator('[data-view=atlas]').click();page.locator('#atlas-search').fill('Matrix')
                assert 0<page.locator('.atlas-card').count()<10
                page.locator('#atlas-search').fill('no-such-observatory-instrument')
                assert page.locator('.atlas-card').count()==0
                page.locator('#share-open').click()
                page.locator('#share-topic').select_option('signal')
                page.locator('#share-format').select_option('story')
                assert page.locator('#share-preview').get_attribute('src')=='./share/signal-garden-story.jpg'
                assert '1080 × 1920' in page.locator('#share-status').inner_text()
                assert page.locator('#share-caption').input_value().startswith('Explore') or 'Signal' in page.locator('#share-caption').input_value()
                page.locator('#share-close').click()
                page.locator('[data-view=evidence]').click()
                with page.expect_download() as dl:page.locator('#export-replay').click()
                assert dl.value.suggested_filename=='observatory-replay.json'
                page.locator('#session-date').fill('2026-10-20T12:00')
                with page.expect_download() as calendar:page.locator('#calendar-ics').click()
                assert calendar.value.suggested_filename=='observatory-session.ics'
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                assert not errors,errors
                checks.append({'viewport':name,'status':'PASS','flows':['navigation','zero-overlap','training','replay','invalid-input','preferences','search','share','download','exact-quantum-gates','calendar-export','no-overflow']})
                page.close()
            page=browser.new_page()
            page.goto(base+'/interfaces/civic-assignment/')
            page.locator('[data-observatory-doorway] button').click()
            assert page.locator('.observatory-embed-dialog').is_visible()
            embedded=page.frame_locator('.observatory-embed-dialog iframe')
            embedded.locator('[data-view=signal]').click()
            assert embedded.locator('#view-signal').is_visible()
            page.locator('.observatory-embed-bar button').click()
            assert not page.locator('.observatory-embed-dialog').is_visible()
            checks.append({'integration':'same-origin iframe doorway','status':'PASS'})
            browser.close()
    finally:
        server.shutdown();server.server_close()
    report={'status':'PASS','checks':checks}
    (ROOT/'website/interfaces/observatory/qa.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
