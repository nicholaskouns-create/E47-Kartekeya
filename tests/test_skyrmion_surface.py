from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
html=(root/'website/interfaces/skyrmion/index.html').read_text()
js=(root/'website/interfaces/skyrmion/skyrmion.js').read_text()
terrain=(root/'website/interfaces/skyrmion/terrain-3d.js').read_text()
assets=(root/'website/interfaces/skyrmion/licensed-aircraft-assets.js').read_text()
licenses=(root/'website/interfaces/skyrmion/ASSET_LICENSES.md').read_text()
prov=json.loads((root/'website/interfaces/skyrmion/provenance.json').read_text())

def test_surface():
    assert 'SKYRMION' in html
    for token in ['F-16','SR-71','X-15','EIDOLON','MANTA','SYNTAX JACOB']:
        assert token in html or token in js
    for token in ['Las Vegas','Los Angeles','New York','Tokyo','Everest','Start flight']:
        assert token in html

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
    assert 'skyrmion:manta-frame' in html

def test_elevation_aware_terrain3d():
    assert 'terrain-3d.js' in html
    assert 'terrain-renderer.js' not in html
    for token in ['World_Imagery','terrain-tiles','makeBuildings','makeClouds','makeLights','updateCamera','samplePatchHeight','pitch','roll']:
        assert token in terrain

def test_threejs_vehicle_fleet():
    for token in ['makeF16','makeSR71','makeX15','makeEidolon','makeManta','makeSyntaxJacob','craftRoot','updateMantaFrame']:
        assert token in terrain
    assert 'CITY_SKYRMION_TERRAIN3D?.ready' in html
    assert "schema:'SKYRMION-TERRAIN-3D-6.1'" in terrain

def test_high_detail_vehicle_systems():
    for token in ['physicalGlass','pivotSurface','landingGear','engineFlame','makeTrailSystem','updateCraftSystems','castShadow','receiveShadow','shadowTarget']:
        assert token in terrain
    for token in ['aileronL','aileronR','elevatorL','elevatorR','flapL','flapR','spoilerL','spoilerR']:
        assert token in terrain
    assert 'skyrmionBindRotation' in terrain
    assert 'animationMixer' in terrain

def test_render_quality_governor():
    for token in ['applyQualityScale','city:render-scale','quality.renderScale','shadowSize','skyrmion:render-stats']:
        assert token in terrain
    assert 'renderer.shadowMap.enabled=atmospheric' in terrain
    assert 'scene.fog.density' in terrain

def test_licensed_aircraft_pipeline():
    assert 'licensed-aircraft-assets.js' in terrain
    assert 'Identity gate' in terrain
    assert 'SKYRMION-TERRAIN-3D-6.1' in terrain
    for token in ['f15-polyducky','nasa-global-hawk','amvlab-b737-nologo','f16-cdesrocher','sr71-manilov','x15-cmoreau']:
        assert token in assets
    for token in ['GLTFLoader','SkeletonUtils.js','collectModelStats','validateAssetRecord','auditLicensedAssets','GLB load timeout']:
        assert token in assets
    assert 'runLicensedAssetAudit' in terrain
    assert 'NASA Media Usage Guidelines' in assets
    assert 'CC BY 4.0' in assets
    assert 'runtimeUrl:null' in assets
    assert 'must not become F-16, SR-71, or X-15' in licenses

def test_identity_gate_preserves_named_fleet():
    assert 'canReplaceCraft' in assets
    assert 'meta?.runtimeUrl&&meta?.exactFor&&meta.exactFor===craftName' in assets
    assert 'exactFor:"F-16"' in assets
    assert 'exactFor:"SR-71"' in assets
    assert 'exactFor:"X-15"' in assets
    # Exact candidates are intentionally not runtime-downloadable until provider-authorized materialization.
    for asset_id in ['f16-cdesrocher','sr71-manilov','x15-cmoreau']:
        record=assets.split('"'+asset_id+'"',1)[1].split('})',1)[0]
        assert 'runtimeUrl:null' in record

def test_asset_license_register():
    for token in ['NASA Global Hawk','amvlab-b737-nologo','f16-cdesrocher','sr71-manilov','x15-cmoreau','Creative Commons Attribution 4.0']:
        assert token in licenses
    assert 'does not alter the authoritative flight-state' in licenses


def test_resilient_boot_and_hero_framing():
    boot=(root/'website/interfaces/skyrmion/runtime2/bootstrap.js').read_text()
    assert 'SKYRMION-TERRAIN-3D-6.1' in terrain
    assert "getLicensedAssetModule" in terrain
    assert "from './licensed-aircraft-assets.js'" not in terrain
    assert 'PerspectiveCamera(47' in terrain
    assert 'MeshPhysicalMaterial' in terrain
    assert 'addNavigationLights' in terrain
    assert 'cameraDistance:31' in terrain
    assert 'cameraDistance:48' in terrain
    assert 'cameraDistance:39' in boot
    assert 'src="./runtime2/bootstrap.js"' in html
    assert 'await createSkyrmionTerrain3D' not in html


def test_runtime2_boot_syntax_regressions():
    boot=(root/'website/interfaces/skyrmion/runtime2/bootstrap.js').read_text()
    assert 'keys.control?.35:.72' not in boot
    assert 'keys.control ? .35 : .72' in boot
    assert 'SKYRMION-VISUAL-FALLBACK-1.0' in boot


def test_stable_chase_camera():
    assert 'SKYRMION-TERRAIN-3D-6.1' in terrain
    assert 'cameraForward.set(0,0,-1).applyQuaternion' in terrain
    assert 'bankMix:.10' in terrain
    assert 'cameraGround+5.5' in terrain
    assert 'oldLocal=localMeters(patch.center' in terrain
    assert 'speedFactor*55' not in terrain


def test_stable_flight_controls_and_yaw():
    runtime=(root/'website/interfaces/skyrmion/runtime2/runtime2.js').read_text()
    vehicles=(root/'website/interfaces/skyrmion/runtime2/vehicle-registry.js').read_text()
    boot=(root/'website/interfaces/skyrmion/runtime2/bootstrap.js').read_text()
    assert 'SKYRMION-RUNTIME-2.1' in runtime
    assert 'commandControls' in runtime
    assert '_updateFlightControls' in runtime
    assert '+beta*(f.betaDamp??1.25)' in runtime
    assert '-r*(f.yawDamp??.8)' in runtime
    assert 'yawRate' in vehicles
    assert 'function shapeAxis' in boot
    assert 'keyYaw*.46' in boot


def test_supabase_world_registry_pipeline():
    registry=(root/'website/interfaces/skyrmion/world-registry.js').read_text()
    world=json.loads((root/'website/interfaces/skyrmion/world-data.json').read_text())
    assert 'SKYRMION-TERRAIN-3D-6.2' in terrain
    assert 'skyrmion-world-runtime' in registry
    assert 'SKYRMION-WORLD-RUNTIME-2.0' in registry
    assert 'loadWorldRegistry' in terrain
    assert 'TILE_BLOB_CACHE' in terrain
    assert 'compositeHillshade' in terrain
    assert 'nearestPlaces' in terrain
    assert 'id="mapStatus"' in html
    assert world['schema']=='SKYRMION-WORLD-DATA-2.0'
    assert 'gps_map_sources' in world['map_runtime']['database_tables']
    assert world['terrain']['encoding']=='mapbox-terrain-rgb'
