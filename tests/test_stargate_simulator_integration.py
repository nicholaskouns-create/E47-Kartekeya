from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT/'website/interfaces/shared/stargate-invariants.js'
FLIGHT=ROOT/'website/interfaces/flight'
SKYR=ROOT/'website/interfaces/skyrmion'
SYNTAX=ROOT/'website/interfaces/syntax-jacob'

def test_shared_stargate_formalism_boundaries():
    s=SHARED.read_text()
    assert "STARGATE-SIMULATOR-INVARIANTS-1.0" in s
    assert "omega_c:47/125" in s
    assert "sech4_integral:4/3" in s
    assert "physicalWormholeValidated:false" in s
    assert "empiricalNECViolationValidated:false" in s
    assert "hardwareStargateValidated:false" in s
    assert "e47RankFractionIsPhysicalThreshold:false" in s
    assert "staticHessianImpliesLorentzianStability:false" in s

def test_all_flight_wrappers_receive_shared_bridge():
    shell=(FLIGHT/'flight-shell.js').read_text()
    assert "../shared/stargate-invariants.js" in shell
    assert "installStargateInvariantBridge" in shell
    for name in ["hover-assembly","mav","eidolon-harmonic","eidolon","hover-cockpit"]:
        html=(FLIGHT/name/'index.html').read_text()
        assert 'type="module" src="../flight-shell.js"' in html

def test_native_ufo_receives_stargate_without_double_boot():
    html=(FLIGHT/'ufo-propulsion/index.html').read_text()
    js=(FLIGHT/'ufo-propulsion/native-ufo.js').read_text()
    assert html.count('src="./native-ufo.js"') == 1
    assert "../../shared/stargate-invariants.js" in js
    assert "installStargateInvariantBridge" in js
    assert "modeled_observables" not in js  # supplied through shared typed packet

def test_syntax_jacob_stargate_receipt_binding():
    app=(SYNTAX/'app.js').read_text()
    component=json.loads((SYNTAX/'component.json').read_text())
    provenance=json.loads((SYNTAX/'provenance.json').read_text())
    assert component["version"]=="1.3.0"
    assert "../shared/stargate-invariants.js" in app
    assert "stargate:stargate.packet()" in app
    assert provenance["runtime"]["stargate_invariants"]["physical_promotion"] is False

def test_skyrmion_stargate_telemetry_and_proof_binding():
    runtime=(SKYR/'runtime2/runtime2.js').read_text()
    bootstrap=(SKYR/'runtime2/bootstrap.js').read_text()
    component=json.loads((SKYR/'component.json').read_text())
    assert component["version"]=="2.4.0"
    assert "SKYRMION-RUNTIME-2.3" in runtime
    assert "createStargatePacket" in runtime
    assert "stargate:d.stargate" in runtime
    assert "STARGATE · 47/125 · OPEN" in bootstrap

def test_manifest_registers_shared_stargate_formalism():
    manifest=json.loads((ROOT/'lab-manifest.json').read_text())
    sg=manifest["shared_formalisms"]["stargate"]
    assert sg["module"]=="website/interfaces/shared/stargate-invariants.js"
    assert sg["certificate"]=="MC-STARGATE-CORRECTED-20260919"
    assert "physical closure open" in sg["evidence_boundary"]
