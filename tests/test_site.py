"""Test fixtures are synthetic and never distributed as real Eurostat measurements."""
import gzip
import io
import os
import socket
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[1]

def fixture():
    years=range(2016,2026)
    keys=[f'{y}-W{w:02}' for y in years for w in range(1,53)]+['2020-W53']
    header='freq,unit,sex,age,geo\\TIME_PERIOD\t'+'\t'.join(keys)
    rows=[header]
    ages=['Y_LT5']+[f'Y{x}-{x+4}' for x in range(5,100,5)]+['Y_GE100']
    assert len(ages)==21
    for geo in ['IS','NO','SE','FI','DK','ES']:
        for age in ages:
            vals=[]
            for label in keys:
                y=int(label[:4]);base=100
                if y in (2016,2017,2018,2019):value=base
                elif y==2020:value=110
                elif y==2021:value=120
                elif y==2022:value=95
                elif y==2023:value=105
                elif y==2024:value=110
                else:value=115
                if label=='2020-W53':value=999999
                if geo=='ES' and age=='Y_LT5' and label=='2025-W10':vals.append(':');continue
                vals.append(f'{value} p' if y==2025 else f'{value} ')
            rows.append(f'W,NR,T,{age},{geo}\t'+'\t'.join(vals))
    return gzip.compress(('\n'.join(rows)+'\n').encode())


def run():
    raw=fixture()
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    proc=subprocess.Popen(['python','-m','http.server',str(port),'--bind','127.0.0.1'],cwd=BASE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        time.sleep(.7)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
            page.route('**/data/demo_r_mwk_05.tsv.gz',lambda route:route.fulfill(body=raw,status=200,content_type='application/gzip',headers={'Access-Control-Allow-Origin':'*'}))
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content((BASE/'index.html').read_text(),wait_until='domcontentloaded');page.evaluate('''(txt) => window.__eurostatQA.adoptTest(window.__eurostatQA.processTSV(txt))''',gzip.decompress(raw).decode());page.locator('.status.ok').wait_for(timeout=15000)
            values=page.evaluate('''() => ({
             codes: window.__eurostatQA.getData().countryCodes,
             iceland: window.__eurostatQA.getData().countries.IS.annual.total,
             spain: window.__eurostatQA.getData().countries.ES.annual.total[2025],
             selected: [...document.querySelectorAll('.country.on')].map(e=>e.textContent),
             chartPaths: document.querySelectorAll('#line-chart path').length,
             stats: [...document.querySelectorAll('.stat-number')].map(x=>x.textContent),
             infographics: document.querySelectorAll('.info-card').length
            })''')
            print('TEST OUTPUT:',values)
            assert not errors,errors
            assert len(values['codes'])==6
            assert len(values['selected'])==5
            assert values['chartPaths']==5
            assert abs(values['iceland']['2020']['pct']-10)<1e-7
            assert abs(values['iceland']['2021']['pct']-20)<1e-7
            assert abs(values['iceland']['2022']['pct']+5)<1e-7
            assert abs(values['iceland']['2025']['pct']-15)<1e-7
            assert values['spain']['complete'] is False
            assert values['infographics']==2
            assert all(values['stats'])
            page.screenshot(path='/mnt/data/umframdaudi_desktop_preview.png',full_page=True)
            page.set_viewport_size({'width':390,'height':840});page.screenshot(path='/mnt/data/umframdaudi_mobile_preview.png',full_page=True)
            page.locator('#preset-none').click();assert page.locator('#line-chart .chart-empty').count()==1
            page.locator('#preset-all').click();assert page.locator('#line-chart path').count()==6
            page.locator('#search').fill('spánn');assert page.locator('#other-buttons .country').count()==1
            with page.expect_download() as dl:
                page.locator('#download-info-svg').click()
            downloaded=dl.value
            assert downloaded.suggested_filename=='island_umframdaudi_2020_2025.svg'
            assert downloaded.path().stat().st_size>3000
            reorder=[]
            for idx,line in enumerate(gzip.decompress(raw).decode().splitlines()):
                if idx==0: reorder.append(line.replace('freq,unit,sex,age,geo\\TIME_PERIOD','freq,age,sex,unit,geo\\TIME_PERIOD'))
                else:
                    a,b=line.split('\t',1);v=a.split(',');reorder.append(','.join([v[0],v[3],v[2],v[1],v[4]])+'\t'+b)
            parsed=page.evaluate('''txt => window.__eurostatQA.processTSV(txt).countries.IS.annual.total[2020].pct''','\n'.join(reorder)+'\n')
            assert abs(parsed-10)<1e-7
            print('PASS: parsing, dimension permutations, export, controls, completeness rules, visual rendering')
            browser.close()
    finally:proc.terminate();proc.wait()

if __name__=='__main__':run()
