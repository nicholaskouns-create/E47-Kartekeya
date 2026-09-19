from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
html=(root/'website/interfaces/skyrmion/index.html').read_text()
js=(root/'website/interfaces/skyrmion/skyrmion.js').read_text()
prov=json.loads((root/'website/interfaces/skyrmion/provenance.json').read_text())
def test_surface():
    assert 'SKYRMION' in html
    for token in ['F-16','SR-71','X-15','EIDOLON','MANTA','SYNTAX JACOB']:
        assert token in js
def test_city_bindings():
    for token in ['matrix-cube-adapter','city-graphics-accelerator','syntax-jacob-ephemeris','aetheris.receipt','47/125']:
        assert token in js
def test_boundary():
    assert 'simulation-only' in js
    assert prov['schema']=='CITY-INVARIANT/1.0'
    assert 'human canonical-promotion gate remains external and unchanged' in prov['invariant']
