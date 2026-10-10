"""Optional browser QA. Install Playwright separately; pass a local preview URL."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import tempfile

from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8765/interfaces/e47-research-workbench/')
    parser.add_argument('--screenshots',type=Path)
    args=parser.parse_args()
    with sync_playwright() as p, tempfile.TemporaryDirectory() as scratch:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1080},accept_downloads=True)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        page.goto(args.url)
        page.wait_for_function("document.getElementById('notice').textContent.includes('Run complete')")
        assert page.locator('#samples tr').count()==6
        if args.screenshots:
            args.screenshots.mkdir(parents=True,exist_ok=True)
            page.screenshot(path=str(args.screenshots/'desktop.png'),full_page=True)
        page.locator('#preset').select_option('seeded')
        page.locator('#seed').fill('125');page.locator('#seed').dispatch_event('change')
        page.locator('#run').click()
        with page.expect_download() as event:page.locator('#export-json').click()
        path=Path(scratch)/'run.json';event.value.save_as(path)
        run=json.loads(path.read_text());assert len(run['records'])==221
        assert run['kernel_weight']!=.376
        run['inputs']['epsilon']*=.7;run['records'][0]['error']=999
        path.write_text(json.dumps(run));page.locator('#import-file').set_input_files(path)
        page.wait_for_function("document.getElementById('epsilon').value==='imported'")
        page.locator('#run').click()
        with page.expect_download() as event:page.locator('#export-json').click()
        replay=Path(scratch)/'replay.json';event.value.save_as(replay)
        result=json.loads(replay.read_text());assert result['inputs']['epsilon']==run['inputs']['epsilon']
        assert result['records'][0]['error']!=999
        for button,filename in [('export-csv','samples.csv'),('export-md','note.md')]:
            with page.expect_download() as event:page.locator('#'+button).click()
            output=Path(scratch)/filename;event.value.save_as(output);assert output.stat().st_size>100
        page.locator('#preset').select_option('selected');assert page.locator('#final-error').inner_text()=='0.00000'
        page.locator('#preset').select_option('complement');assert 'No initial selected' in page.locator('#notice').inner_text()
        page.locator('#mode').select_option('continuous');page.locator('#horizon').fill('1');page.locator('#run').click()
        page.locator('#preset').select_option('isotropic');assert page.locator('#run-label').inner_text()=='CONTINUOUS'
        page.locator('[data-view="geometry"]').click();page.locator('#facet').select_option('46')
        assert page.locator('#facet-info').inner_text().find('Magnetic index m')>=0
        page.locator('#crystal').focus();page.keyboard.press('ArrowRight')
        with page.expect_download() as event:page.locator('#export-obj').click()
        mesh=Path(scratch)/'mesh.obj';event.value.save_as(mesh)
        text=mesh.read_text();assert sum(line.startswith('v ') for line in text.splitlines())==90
        assert sum(line.startswith('f ') for line in text.splitlines())==47
        if args.screenshots:page.screenshot(path=str(args.screenshots/'geometry.png'),full_page=True)
        page.locator('[data-view="validation"]').click();page.locator('#verify').click()
        assert 'Browser verification passed' in page.locator('#notice').inner_text()
        assert page.locator('#checks tr').count()==13
        page.locator('[data-view="workspace"]').click();assert page.locator('.workspace-card').count()>=4
        page.set_viewport_size({'width':390,'height':844})
        page.locator('[data-view="dynamics"]').click()
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
        if args.screenshots:page.screenshot(path=str(args.screenshots/'mobile.png'),full_page=True)
        assert not errors,errors
        # Invalid user input must be safely rejected and leave previous results intact.
        invalid=Path(scratch)/'invalid.json';invalid.write_text('{"schema":"E47-WORKBENCH-RUN-1.0","version":"1.0.0","inputs":{"weights":[0,0,0,0,0,0,0]}}')
        page.locator('#import-file').set_input_files(invalid)
        page.wait_for_function("document.getElementById('notice').classList.contains('error')")
        assert 'positive weight' in page.locator('#notice').inner_text()
        assert len(errors)==1 and 'interaction' in errors[0]
        browser.close()
        print('BROWSER QA PASS: desktop/mobile; discrete/continuous; seed; all exports; custom-step import/recompute; geometry controls; ledger; workspace links; invalid import; no unexpected JS or CSP errors.')


if __name__=='__main__':main()
