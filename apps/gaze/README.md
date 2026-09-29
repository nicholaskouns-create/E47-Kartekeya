# Gaze — House Observatory

[Open the browser app](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/gaze/)

The supplied Streamlit instrument is repaired in `app.py`. Run from the repository root:

```sh
python -m pip install -r apps/gaze/requirements.txt
streamlit run apps/gaze/app.py
```

GitHub Pages publishes `website/interfaces/gaze/`, a standalone browser implementation using bundled Astronomy Engine 2.1.19 (MIT). Notion embeds that URL. No Python server is needed for the public version. The Streamlit source is available separately for a Python host.

Both versions track Polaris, Vega, Deneb, Sirius, Moon, Jupiter, Saturn and Venus with location controls, a fixed-baseline ±24 hour/day scrubber, a zenith-centered sky plot, and great-circle Moon–Jupiter separation. Azimuth is clockwise from true north; refraction is disabled. The star coordinates are the supplied fixed catalog; proper motion is not propagated. Browser star distances are set to 10^9 light-years to make parallax negligible, matching the direction-only Python catalog; these are computational placeholders, not measured distances.

Python uses Astropy builtin ERFA solar-system ephemerides and bundled IERS Earth-orientation data. Browser uses Astronomy Engine's own models and Delta-T approximation. They are independent approximate implementations, not identical DE430 calculations. Python surfaces accuracy warnings. The E47 badge is the exact rank fraction only; no coherence measurement or projector inner product is implemented.

Repairs: completed missing polar array values, corrected Plotly hover API, eliminated silent body failures and fabricated fallback coordinates, replaced flat alt–az distance with spherical separation, fixed longitude labeling, and removed unsupported calibration claims. Runtime dependencies are confined to this app.
