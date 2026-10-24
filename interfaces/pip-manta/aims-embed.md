# AIMS embed · PIP E47–MANTA

Canonical app:
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/pip-manta/

Responsive wrapper:
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/pip-manta/embed.html

Long portal card:
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/pip-manta/card.html

The frame loads `?embed=1`. The explainer reports its height. The wrapper measures the same document directly and relays `{source:"pip-manta", type:"resize", height}` to the parent. A parent that ignores the message still gets a 980px frame and an internal scroll, not a clipped Pip.

## Full interactive embed

Paste this as one block. The script is the size contract. Without it, the frame stays at 980px and scrolls inside itself.

```html
<div id="pip-manta-slot" style="width:100%;min-height:760px;background:#071428;border-radius:16px;overflow:auto;">
  <iframe
    id="pip-manta-frame"
    src="https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/pip-manta/embed.html"
    title="PIP Explains E47–MANTA"
    loading="eager"
    allow="fullscreen"
    allowfullscreen
    referrerpolicy="origin"
    style="width:100%;height:980px;min-height:760px;border:0;background:#071428;display:block;">
  </iframe>
</div>
<script>
window.addEventListener("message", function (e) {
  var d = e.data;
  if (!d || d.source !== "pip-manta" || d.type !== "resize") return;
  var frame = document.getElementById("pip-manta-frame");
  if (!frame || !d.height) return;
  frame.style.height = Math.max(760, Math.ceil(d.height)) + "px";
});
</script>
```

## Long-and-skinny portal card embed

```html
<div style="width:100%;height:244px;background:#071428;border-radius:16px;overflow:hidden;">
  <iframe
    src="https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/pip-manta/card.html"
    title="PIP E47–MANTA portal card"
    loading="lazy"
    referrerpolicy="origin"
    style="width:100%;height:244px;border:0;background:#071428;display:block;">
  </iframe>
</div>
```

Evidence boundary remains unchanged: E0/E1 exact finite algebra is separated from E2 morph / force / torque / trajectory simulation.
