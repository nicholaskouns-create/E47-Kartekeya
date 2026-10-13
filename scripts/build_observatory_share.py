#!/usr/bin/env python3
"""Rebuild the Observatory social kit locally with Pillow; no network needed."""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1] / 'website/interfaces/observatory/share'
URL = 'https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/observatory/'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
VARIANTS = [
 ('city-observatory', 'City\nObservatory', 'Complex ideas. Playable worlds.', 'Explore connected instruments, experiments and evidence.', 'Explore the City Observatory: complex ideas made playable, with experiments you can inspect and share.', 'city'),
 ('signal-garden', 'Signal\nGarden', '125 dimensions. 47 retained.', 'Shape a signal. Project it. Compare the result.', 'Explore Signal Garden: a 125-to-47 spectral projection experiment. Change the signal and compare its components.', 'signal'),
 ('neural-lab', 'Neural\nLab', 'Make a prediction. Then test it.', 'Train, compare and discover what changed.', 'Play with learning in Neural Lab. Train a small network, compare runs and inspect what changed.', 'neural'),
 ('evidence-atlas', 'Evidence\nAtlas', 'Follow the idea to its evidence.', 'Inspect sources, assumptions and replayable results.', 'Visit Evidence Atlas to explore sources, assumptions and replayable results behind the instruments.', 'atlas')
]
FORMATS = [('og',1200,630,['Open Graph','LinkedIn','Facebook']),('square',1080,1080,['Instagram feed','Threads']),('story',1080,1920,['Instagram Stories','TikTok cover']),('landscape',1200,675,['X','Bluesky'])]

def font(size, serif=False): return ImageFont.truetype(SERIF if serif else SANS, int(size))
def render(slug,title,tag,desc,caption,kind,fmt,w,h):
 im=Image.new('RGB',(w,h),'#08131e'); d=ImageDraw.Draw(im)
 s=w/1200; pad=int(70*s); tall=h>w
 # Restrained radial atmosphere, keeping all content inside platform safe margins.
 for y in range(h):
  t=y/h; d.line((0,y,w,y),fill=(8+int(5*t),19+int(10*t),30+int(9*t)))
 random.seed(47)
 for _ in range(70):
  x=random.randrange(w); y=random.randrange(h); r=random.choice([1,1,2]); d.ellipse((x-r,y-r,x+r,y+r), fill='#36535f')
 d.line((pad,pad,w-pad,pad),fill='#35535d',width=max(1,int(s)))
 d.text((pad,pad+20*s),'E47  /  PLAY · EXPLORE · VERIFY',font=font(17*s),fill='#b2d6cd')
 ty=int(h*.18) if tall else int(h*.20)
 heading=font(94*s if tall else 75*s,True)
 d.multiline_text((pad,ty),title,font=heading,fill='#e4f2df',spacing=int(5*s))
 textbottom=ty+int((220 if tall else 185)*s)
 d.text((pad,textbottom),tag,font=font(25*s),fill='#efae78')
 # Motif appears below text in portrait layouts and to the right in landscape.
 cx=w*.5 if tall else w*.78; cy=h*.65 if tall else h*.48
 radius=w*.29 if tall else w*.16
 pts=[]
 for layer in range(5):
  for j in range(5):
   a=2*math.pi*j/5+layer*.24; rr=radius*(.26+layer*.18)
   pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.85))
 for i,p in enumerate(pts):
  for k in (5,6):
   if i+k<len(pts): d.line((*p,*pts[i+k]),fill='#315461',width=max(1,int(2*s)))
 for i,(x,y) in enumerate(pts):
  r=(5 if i%3 else 8)*s; col='#7cddd8' if i%3 else '#edaa73'
  d.ellipse((x-r,y-r,x+r,y+r),fill=col)
 if kind=='signal':
  d.text((int(cx-radius*.68),int(cy-radius*.1)),'125 → 47',font=font(32*s),fill='#e4f2df')
 elif kind=='neural':
  d.text((int(cx-radius*.63),int(cy-radius*.1)),'LEARN / COMPARE',font=font(18*s),fill='#e4f2df')
 elif kind=='atlas':
  d.text((int(cx-radius*.6),int(cy-radius*.1)),'SOURCE → REPLAY',font=font(18*s),fill='#e4f2df')
 footer=h-int(130*s) if not tall else h-int(310*s)
 d.line((pad,footer,w-pad,footer),fill='#35535d',width=max(1,int(s)))
 d.text((pad,footer+22*s),desc,font=font(18*s),fill='#b2d6cd')
 d.text((pad,footer+57*s),'nicholaskouns-create.github.io / E47-Kartekeya',font=font(15*s),fill='#84a5ac')
 path=ROOT/f'{slug}-{fmt}.jpg'; im.save(path,quality=90,optimize=True,subsampling=0)
 return {'id':f'{slug}-{fmt}','variant':slug,'format':fmt,'file':path.name,'mime_type':'image/jpeg','width':w,'height':h,'platforms':dict((x,{'suggested_use':fmt}) for x in next(f[3] for f in FORMATS if f[0]==fmt)),'caption':caption+' '+URL,'alt':f'{title.replace(chr(10)," ")}: {tag} A cyan and orange constellation on a midnight background. '+desc,'canonical_url':URL,'bytes':path.stat().st_size}

def main():
 ROOT.mkdir(parents=True,exist_ok=True)
 assets=[render(*v,*f[:3]) for v in VARIANTS for f in FORMATS]
 (ROOT/'manifest.json').write_text(json.dumps({'schema_version':1,'title':'City Observatory social share kit','canonical_url':URL,'default_asset':'city-observatory-og.jpg','assets':assets},indent=2)+'\n')
 (ROOT/'README.md').write_text('''# Observatory share kit\n\nChoose a content variant and export size in `manifest.json`. Each entry supplies a ready-to-copy caption, descriptive alt text, platform suggestions and the precise destination URL. Upload the image to your chosen platform, paste the caption, then add its alt text. Story posts need a link sticker pointing to the canonical URL; an image alone is not a clickable link. Suggested sizes do not imply that every platform preserves a full image without cropping.\n\nAll images are deterministic JPEG graphics, with no remote assets or generated scientific claims. Rebuild with `python scripts/build_observatory_share.py` after installing Pillow.\n\nVariants: City Observatory, Signal Garden, Neural Lab, Evidence Atlas. Sizes: 1200×630 Open Graph; 1080×1080 square; 1080×1920 story; 1200×675 landscape.\n''')
 print(json.dumps({'assets':len(assets),'bytes':sum(a['bytes'] for a in assets),'directory':str(ROOT)}))
if __name__=='__main__': main()
