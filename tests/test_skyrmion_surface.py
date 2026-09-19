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


def test_elevation_aware_terrain3d():
    terrain=(root/'website/interfaces/skyrmion/terrain-3d.js').read_text()
    assert 'terrain-3d.js' in html
    for token in ['World_Imagery','terrain-tiles','makeBuildings','makeClouds','makeLights','updateCamera','pitch','roll']:
        assert token in terrain


def test_threejs_vehicle_fleet():
    terrain=(root/'website/interfaces/skyrmion/terrain-3d.js').read_text()
    for token in ['makeF16','makeSR71','makeX15','makeEidolon','makeManta','makeSyntaxJacob','craftRoot','updateMantaFrame','SKYRMION-TERRAIN-3D-2.0']:
        assert token in terrain
    assert "skyrmion:manta-frame" in html
    assert "CITY_SKYRMION_TERRAIN3D?.ready" in html


def test_high_detail_vehicle_systems():
    terrain=(root/'website/interfaces/skyrmion/terrain-3d.js').read_text()
    for token in ['physicalGlass','pivotSurface','landingGear','engineFlame','makeTrailSystem','updateCraftSystems','castShadow','receiveShadow','shadowTarget','SKYRMION-TERRAIN-3D-3.0']:
        assert token in terrain
    for craft in ['makeF16','makeSR71','makeX15','makeEidolon','makeManta','makeSyntaxJacob']:
        assert craft in terrain


def test_licensed_aircraft_pipeline():
    terrain=(root/'website/interfaces/skyrmion/terrain-3d.js').read_text()
    assets=(root/'website/interfaces/skyrmion/licensed-aircraft-assets.js').read_text()
    licenses=(root/'website/interfaces/skyrmion/ASSET_LICENSES.md').read_text()
    assert 'licensed-aircraft-assets.js' in terrain
    assert 'ASSET_LICENSES.md' in str(root/'website/interfaces/skyrmion/ASSET_LICENSES.md')
    assert 'Identity gate' in terrain
    assert 'SKYRMION-TERRAIN-3D-4.0' in terrain
    assert 'f15-polyducky' in assets
    assert 'CC BY 4.0' in assets
    assert 'CC BY 4.0' in licenses
    assert 'auditLicensedAssets' in assets
    assert 'runLicensedAssetAudit' in terrain
    assert 'exactFor:"F-16"' not in assets
    assert 'must not become the F-16' in licenses
