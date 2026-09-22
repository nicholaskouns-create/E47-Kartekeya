# Mathematical City instrument portal

Public route: https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/city-live/

The portal presents the 22 destinations supplied on 22 September 2026. It uses
their actual page titles, distinguishes independent SKYRMION, Hover, and City
editions, and preserves each supplied URL, including query strings and fragments.
The homepage links directly to the portal.

## Editing the collection

1. Edit `website/data/city-portal.json` for names, descriptions, categories,
   destinations, artwork, or source references.
2. Run `python scripts/render_city_portal.py`.
3. Review the rendered `website/interfaces/city-live/index.html` and commit both
   the manifest and rendered page. Template changes belong in
   `scripts/templates/city-portal.html`.

The page has no build or runtime package dependencies. All 22 destinations are
ordinary HTML links before JavaScript loads. JavaScript adds search, five category
filters, alphabetical sorting, grid/list views, and shareable URL filter state.
An unknown category falls back to the full collection. Search supports multiple
terms; `/` focuses it and Escape clears it. Reduced-motion preferences are honored.

## Artwork and sources

Existing artwork is copied locally into `website/assets/city-portal/`. The
manifest records the source provider, stable source reference, and SHA-256 of
each optimized local asset. No temporary Notion or Drive download URLs are
published. Notion supplies the workshop cover and six instrument stills; Google
Drive supplies SCALAR's brand artwork; Supabase supplies CHIMERA's cover; the
remaining cards use their destination's own Open Graph artwork.

Destination metadata and artwork were retrieved on 22 September 2026. All 22
supplied URLs returned HTTP 200. That is a document availability check; runtime
behavior belongs to each instrument. The portal never labels a remote simulation
as tested solely because its HTML returned successfully.

## Verification

```sh
python scripts/render_city_portal.py
node --check website/interfaces/city-live/portal.js
node --test scripts/check_website.cjs scripts/check_e47_bridge.cjs \
  scripts/check_eidolon_receipt_binding.mjs scripts/check_q5_surface.mjs
```

The website's existing GitHub Pages workflow publishes `website/` after its
validation job succeeds. The mathematical core and all simulator code remain
independent of this presentation change.
