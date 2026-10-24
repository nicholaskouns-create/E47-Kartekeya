# Observatory share kit

Choose a content variant and export size in `manifest.json`. Each entry supplies a ready-to-copy caption, descriptive alt text, platform suggestions and the precise destination URL. Upload the image to your chosen platform, paste the caption, then add its alt text. Story posts need a link sticker pointing to the canonical URL; an image alone is not a clickable link. Suggested sizes do not imply that every platform preserves a full image without cropping.

All images are deterministic JPEG graphics, with no remote assets or generated scientific claims. Rebuild with `python scripts/build_observatory_share.py` after installing Pillow.

Variants: City Observatory, Signal Garden, Neural Lab, Evidence Atlas. Sizes: 1200×630 Open Graph; 1080×1080 square; 1080×1920 story; 1200×675 landscape.
