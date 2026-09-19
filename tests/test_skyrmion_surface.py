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


def test_live_manta_and_gps_bridge():
    worker=(root/'website/interfaces/skyrmion/manta-worker.js').read_text()
    gps=(root/'website/interfaces/shared/city-gps-runtime.js').read_text()
    py=(root/'src/manta/programmable_matter.py').read_text()
    assert 'manta-worker.js' in html
    assert 'city-gps-runtime.js' in html
    assert 'MANTA-PYTHON-BRIDGE-1.0' in worker
    assert 'step_packet' in py
    assert 'geometry_nodes' in py
    assert 'CITY-GPS-RUNTIME-1.0' in gps


def test_satellite_terrain_renderer():
    terrain=(root/'website/interfaces/skyrmion/terrain-renderer.js').read_text()
    assert 'terrain-renderer.js' in html
    assert 'World_Imagery' in terrain
    assert 'WGS84' in terrain
    assert 'Imagery © Esri' in terrain
    for token in ['Las Vegas','Los Angeles','New York','Tokyo','Everest','Start flight']:
        assert token in html
