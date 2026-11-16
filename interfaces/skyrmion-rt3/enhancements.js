// Skyrmion RT3 UI enhancements — live telemetry, capability cards, E47 indicator, shared footer
export function installSkyrmionEnhancements({runtime, VEHICLES}) {
  // Live telemetry strip
  const strip = document.createElement('div');
  strip.id = 'liveTelemetry';
  strip.style.cssText = 'position:fixed;left:12px;top:58px;z-index:9;background:rgba(5,16,21,.8);border:1px solid rgba(127,232,214,.4);border-radius:10px;padding:8px 12px;font:600 10px ui-monospace;color:#e9f6f5;backdrop-filter:blur(12px);pointer-events:none';
  strip.innerHTML = '<div>ALT <b id="tlAlt">—</b> m · IAS <b id="tlIas">—</b> · M <b id="tlMach">—</b></div><div>FUEL <b id="tlFuel">—</b> · E47 <b id="tlE47">—</b> · RCPT <b id="tlRcpt">—</b></div>';
  document.body.appendChild(strip);

  // Capability cards overlay on fleet
  const cards = {
    f16: 'Conventional · full aero + gear + fuel',
    sr71: 'Conventional · high-Mach compressible',
    x15: 'Conventional · hypersonic research',
    eidolon: 'Experimental · E47 drive · zero aero load',
    manta: 'Experimental · E47 drive · zero aero load',
    skyrmion: 'Experimental · E47 drive · zero aero load',
    jacob: 'Experimental · E47 drive · zero aero load'
  };
  const fleet = document.getElementById('fleet');
  if (fleet) {
    const note = document.createElement('div');
    note.style.cssText = 'margin-top:8px;font:8px ui-monospace;color:#8fb3b0';
    note.textContent = 'Conventional models use compressible aero + gear + fuel. Experimental (E47) models use spectral drive only — aero load is identically zero. Isolation re-checked every step.';
    fleet.parentElement.appendChild(note);
  }

  // Footer
  const footer = document.createElement('div');
  footer.style.cssText = 'position:fixed;left:12px;bottom:4px;z-index:9;font:7px ui-monospace;color:rgba(205,214,208,.6);pointer-events:auto';
  footer.innerHTML = 'Numerical receipt · integrity only · <a href="https://nicholaskouns-create.github.io/E47-Kartekeya/cite/" style="color:#7fe8d6" target="_blank">Open provenance</a>';
  document.body.appendChild(footer);

  // Update loop
  function update() {
    if (!runtime) return;
    const t = runtime.telemetry?.() || {};
    const alt = document.getElementById('tlAlt');
    const ias = document.getElementById('tlIas');
    const mach = document.getElementById('tlMach');
    const fuel = document.getElementById('tlFuel');
    const e47 = document.getElementById('tlE47');
    const rcpt = document.getElementById('tlRcpt');
    if (alt) alt.textContent = Math.round(t.altitude_m || 0);
    if (ias) ias.textContent = Math.round((t.speed || 0) * 1.94384); // m/s to KIAS approx
    if (mach) mach.textContent = (t.aero?.mach || 0).toFixed(2);
    if (fuel) fuel.textContent = t.mass ? Math.round(t.mass.fuelFraction * 100) + '%' : '—';
    const isExp = t.evidence && t.evidence !== 'conventional';
    if (e47) e47.textContent = isExp ? (t.e47?.coherence?.toFixed(3) || 'DRIVE') : 'AERO';
    if (rcpt) rcpt.textContent = t.proof?.hash?.slice(0, 8) || '—';
  }
  setInterval(update, 200);
}
