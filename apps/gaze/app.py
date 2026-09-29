"""Gaze — House Observatory. Run: streamlit run apps/gaze/app.py"""
from datetime import datetime, timezone, timedelta
import warnings
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_body, solar_system_ephemeris
from astropy.utils import iers
import astropy.units as u

# Reproducible offline operation; stale/out-of-range Earth-orientation warnings
# are surfaced in the UI rather than silently hidden.
iers.conf.auto_download = False
iers.conf.auto_max_age = None
STAR_CATALOG = {
    'Polaris': SkyCoord(ra='02h31m49.09s', dec='+89d15m50.8s', frame='icrs'),
    'Vega': SkyCoord(ra='18h36m56.33s', dec='+38d47m01.2s', frame='icrs'),
    'Deneb': SkyCoord(ra='20h41m25.91s', dec='+45d16m49.2s', frame='icrs'),
    'Sirius': SkyCoord(ra='06h45m08.92s', dec='-16d42m58.0s', frame='icrs'),
}

def calculate(target_dt, lat, lon, height):
    if not np.all(np.isfinite([lat, lon, height])) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError('Location must be finite; latitude ±90°, longitude ±180°.')
    t = Time(target_dt)
    location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=height*u.m)
    frame = AltAz(obstime=t, location=location, pressure=0*u.hPa)
    objects = {}
    with solar_system_ephemeris.set('builtin'):
        coords = {**STAR_CATALOG, **{name.capitalize(): get_body(name, t, location)
                  for name in ['moon', 'jupiter', 'saturn', 'venus']}}
        for name, coord in coords.items():
            h = coord.transform_to(frame)
            objects[name] = {'alt': float(h.alt.degree), 'az': float(h.az.degree),
                             'type': 'Star' if name in STAR_CATALOG else 'Planet/Satellite'}
    return objects

def separation(a, b):
    h1, h2, da = np.radians([a['alt'], b['alt'], a['az']-b['az']])
    return float(np.degrees(np.arccos(np.clip(np.sin(h1)*np.sin(h2)+np.cos(h1)*np.cos(h2)*np.cos(da), -1, 1))))

def main():
    st.set_page_config(page_title='Gaze — House Observatory', layout='centered')
    st.markdown('<style>.stApp{background:#0b0f14;color:#d0d7de}h1,h2,h3{font-family:monospace;color:white}</style>', unsafe_allow_html=True)
    st.sidebar.header('Observatory config')
    lat = st.sidebar.number_input('Latitude (degrees north)', min_value=-90., max_value=90., value=36.1716, format='%.4f')
    lon = st.sidebar.number_input('Longitude (degrees east)', min_value=-180., max_value=180., value=-115.1391, format='%.4f')
    height = st.sidebar.number_input('Elevation (meters)', value=610.)
    if 'baseline' not in st.session_state:
        st.session_state.baseline = datetime.now(timezone.utc)
    if st.sidebar.button('Reset to now'):
        st.session_state.baseline = datetime.now(timezone.utc)
        st.session_state.offset = 0
    st.title('Gaze')
    st.caption('HOUSE OBSERVATORY // E47 · 47 / 125')
    mode = st.radio('Step interval', ['Hours', 'Days'], horizontal=True)
    offset = st.slider('Offset from fixed UTC baseline', -24, 24, 0, key='offset')
    dt = st.session_state.baseline + timedelta(**{mode.lower(): offset})
    try:
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter('always')
            objects = calculate(dt, lat, lon, height)
        for message in dict.fromkeys(str(w.message) for w in recorded):
            st.warning(message)
    except Exception as exc:
        st.error(f'Ephemeris calculation unavailable: {exc}')
        st.stop()
    st.subheader('Sky vector radar space')
    fig = go.Figure()
    for name, pos in objects.items():
        visible = pos['alt'] > 0
        color = '#ff9900' if name == 'Polaris' else '#5294e2' if pos['type'] == 'Star' else '#00ecff'
        fig.add_trace(go.Scatterpolar(
            r=[90-pos['alt']] if visible else [], theta=[pos['az']] if visible else [],
            mode='markers+text', text=[name] if visible else [], textposition='top center',
            marker=dict(size=9, color=color, symbol='circle' if pos['type']=='Star' else 'diamond'),
            name=name, hovertemplate=f"{name}<br>Azimuth: {pos['az']:.2f}°<br>Altitude: {pos['alt']:.2f}°<extra></extra>"))
    fig.update_layout(polar=dict(bgcolor='#0d1117',
        radialaxis=dict(range=[0,90], tickvals=[30,60,90], ticktext=['60° Alt','30° Alt','Horizon']),
        angularaxis=dict(direction='clockwise', rotation=90)), showlegend=False,
        template='plotly_dark', paper_bgcolor='#0b0f14', height=450, margin=dict(l=40,r=40,t=35,b=35))
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Projected UTC: {dt.isoformat()} · Site: {lat:.4f}° N, {lon:.4f}° E")
    st.caption('CURRENT SNAPSHOT' if offset == 0 else f'OFFSET TIME-LOCK: {offset:+} {mode}')
    c1, c2 = st.columns(2)
    c1.metric('Moon ↔ Jupiter spherical separation', f"{separation(objects['Moon'], objects['Jupiter']):.2f}°")
    c2.metric('Polaris azimuth / altitude', f"{objects['Polaris']['az']:.2f}° / {objects['Polaris']['alt']:.2f}°")
    target = st.selectbox('Inspect target', list(objects))
    st.json(objects[target])
    st.dataframe([{'name':name, **pos, 'horizon':'ABOVE' if pos['alt']>0 else 'BELOW'} for name,pos in objects.items()], hide_index=True)
    st.caption('Astropy builtin ERFA ephemeris; topocentric AltAz; true-north azimuth; refraction off. Fixed ICRS catalog, no proper motion. Bundled IERS data, automatic downloads off; any accuracy warnings appear above. No DE430 comparison or sky-to-E47 projector is computed.')

if __name__ == '__main__':
    main()
