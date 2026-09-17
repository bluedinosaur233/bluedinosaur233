"""Build the GitHub-compatible visuals. Requires Pillow and a system Arial font."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from math import sin, cos, pi, exp

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/profile-v2'
OUT.mkdir(parents=True,exist_ok=True)
W,H=1440,740
INK='#242832';CYAN='#25ADD4';BLUE='#4F80D5';PINK='#D8488F';MUTED='#7D899B';LINE='#DAE2EE'
FONT=Path('/System/Library/Fonts/Supplemental')

def font(size,bold=False,italic=False):
 name='Arial Bold Italic.ttf' if italic else 'Arial Bold.ttf' if bold else 'Arial.ttf'
 return ImageFont.truetype(str(FONT/name),size)

def text(draw,xy,value,size=18,fill=INK,bold=False,italic=False):
 draw.text(xy,value,font=font(size,bold,italic),fill=fill,anchor='lt')

def tracked(draw,xy,value,size=12,gap=2,fill=MUTED):
 x,y=xy;f=font(size)
 for char in value:
  draw.text((x,y),char,font=f,fill=fill,anchor='lt')
  x+=draw.textlength(char,font=f)+gap

def gradient_text(im,xy,value,size,width=None):
 f=font(size,True,True);box=f.getbbox(value);tw=int(f.getlength(value))+20;th=box[3]-box[1]+15
 mask=Image.new('L',(tw,th));ImageDraw.Draw(mask).text((4,-box[1]),value,font=f,fill=255)
 if width:mask=mask.resize((width,th),Image.Resampling.LANCZOS);tw=width
 grad=Image.new('RGB',(tw,th));d=ImageDraw.Draw(grad)
 stops=[(0,(27,178,214)),(.48,(92,131,207)),(1,(212,61,134))]
 for x in range(tw):
  p=x/max(1,tw-1);a,b=(stops[0],stops[1]) if p<.48 else (stops[1],stops[2]);q=(p-a[0])/(b[0]-a[0]);c=tuple(round(u+(v-u)*q) for u,v in zip(a[1],b[1]));d.line((x,0,x,th),fill=c)
 im.paste(grad,xy,mask)

SCENES=[ROOT/'assets/anime-hero.jpg']+[ROOT/'design/gallery'/f'scene-{i}.jpg' for i in range(1,4)]

def panel_for(scene,size,mobile=False):
 art=ImageOps.exif_transpose(Image.open(SCENES[scene])).convert('RGB')
 if scene==0:
  art=art.crop((150,0,1220,900))
  return ImageOps.fit(art,size,method=Image.Resampling.LANCZOS,centering=(.46,.38))
 # Keep the full landscape composition over a softly extended backdrop.
 backdrop=ImageOps.fit(art,size,method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(24))
 backdrop=Image.blend(backdrop,Image.new('RGB',size,'#EAF0FA'),.45)
 fitted=ImageOps.contain(art,size,method=Image.Resampling.LANCZOS)
 backdrop.paste(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2))
 return backdrop

def create_hero(scene=0):
 im=Image.new('RGB',(W,H));pix=im.load()
 for y in range(H):
  for x in range(W):
   blue=exp(-(((x-1240)/650)**2+((y-50)/520)**2));pink=exp(-(((x-840)/650)**2+((y-690)/360)**2))
   pix[x,y]=(round(248-17*blue+1*pink),round(250-9*blue-13*pink),round(253-4*blue-6*pink))
 d=ImageDraw.Draw(im)
 for x in range(0,W,32):d.line((x,0,x,H),fill='#E9EDF5',width=1)
 for y in range(0,H,32):d.line((0,y,W,y),fill='#E9EDF5',width=1)
 # Wide translucent white layer quiets the grid on the reading side.
 fade=Image.new('RGBA',(W,H));fd=ImageDraw.Draw(fade)
 for x in range(W):fd.line((x,0,x,H),fill=(249,251,253,int(140*(1-x/W))))
 im=Image.alpha_composite(im.convert('RGBA'),fade).convert('RGB');d=ImageDraw.Draw(im)
 d.rectangle((55,36,62,43),fill=CYAN)
 tracked(d,(76,35),'ANCUO LOEWE',13,2.5,INK)
 tracked(d,(1223,36),'PERSONAL SPACE',10,1.5)
 d.line((55,72,1386,72),fill=LINE)
 # Secondary grayscale sheet: a controlled offset, rather than a large shadow.
 panel=panel_for(scene,(735,548))
 panel=Image.blend(panel,Image.new('RGB',panel.size,'#D4E7F5'),.09)
 mono=ImageOps.grayscale(panel).convert('RGB');mono=Image.blend(mono,Image.new('RGB',mono.size,'#EDF0F7'),.62)
 mono_mask=Image.new('L',(735,548));ImageDraw.Draw(mono_mask).polygon([(40,0),(730,30),(693,548),(0,518)],fill=255)
 im.paste(mono,(676,114),mono_mask)
 mask=Image.new('L',(735,548));ImageDraw.Draw(mask).polygon([(35,0),(735,0),(694,548),(0,548)],fill=255)
 im.paste(panel,(659,132),mask)
 d=ImageDraw.Draw(im);d.line([(694,132),(1394,132),(1353,680),(659,680),(694,132)],fill='#A4B4CA',width=1)
 d.line([(681,115),(1386,95),(1413,635)],fill='#B8C6D9',width=1)
 d.rectangle((59,133,86,140),fill=CYAN);d.rectangle((92,133,99,140),fill=PINK)
 text(d,(51,185),'WELCOME',102,bold=True,italic=True)
 text(d,(50,299),'TO MY',105,bold=True,italic=True)
 gradient_text(im,(49,414),'WORLD.',116,width=586)
 d=ImageDraw.Draw(im)
 card=[(1007,579),(1388,579),(1373,665),(992,665)]
 d.polygon([(x+6,y+8) for x,y in card],fill='#BDCBDA')
 d.polygon(card,fill='#FAFBFE',outline=INK)
 d.line((1008,594,1003,623),fill=CYAN,width=5)
 text(d,(1030,594),'NEVER STOP EXPLORING.',16,bold=True,italic=True)
 tracked(d,(1030,626),f'0{scene+1} / 04',10,1.6)
 d.line((1326,622,1351,597),fill=CYAN,width=3)
 d.line((1332,597,1351,597,1351,616),fill=CYAN,width=3)
 d.line((55,702,1386,702),fill='#CCD5E3',width=1)
 tracked(d,(1163,716),'BLUEDINOSAUR233',10,1.6)
 for x in (63,93,123):
  d.line((x,654,x,664),fill='#9DADC2');d.line((x-5,659,x+5,659),fill='#9DADC2')
 if scene==0: im.save(OUT/'hero.png',optimize=True)
 return im

def carousel(slides,path,size):
 # Repaint the small accents throughout each hold, not just at slide changes.
 slides=[im.resize(size,Image.Resampling.LANCZOS) for im in slides]
 frames=[];durations=[]
 for i,im in enumerate(slides):
  for tick in range(51):
   frame=im.copy() if tick<46 else Image.blend(im,slides[(i+1)%len(slides)],(tick-45)/6)
   d=ImageDraw.Draw(frame)
   phase=(i*51+tick)/51
   travel=.5-.5*cos(phase*2*pi)
   if size[0]==1440:
    x=57+round(603*travel)
    d.rectangle((x,700,x+62,703),fill=CYAN)
    for j in range(4):
     h=round(4+10*(.5+.5*sin(phase*2*pi+j*1.6)))
     d.rectangle((143+j*6,665-h,145+j*6,665),fill=BLUE)
   else:
    # The mobile strip follows the same pace along the existing bottom rule.
    d.rectangle((32,846,644,849),fill='#F5F8FC')
    d.line((32,848,644,848),fill=LINE)
    x=32+round(510*travel)
    d.rectangle((x,846,x+101,849),fill=CYAN)
   frames.append(frame);durations.append(100)
 # Full RGB frames avoid GIF's 256-color palette and visible gradient banding.
 temporary=path.with_suffix(path.suffix+'.tmp')
 frames[0].save(temporary,format='WEBP',save_all=True,append_images=frames[1:],duration=durations,loop=0,quality=95,method=6,allow_mixed=True,minimize_size=True)
 temporary.replace(path)

carousel([create_hero(i) for i in range(4)],OUT/'hero.webp',(1440,740))

# Minimal section titles; no decorative descriptions.
for name,label in [('about','ABOUT ME.'),('toolkit','TOOLKIT.'),('activity','GITHUB ACTIVITY.')]:
 for suffix,width,size in [('',1200,46),('-mobile',600,42)]:
  (OUT/f'heading-{name}{suffix}.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="96" viewBox="0 0 {width} 96" role="img"><title>{label}</title><defs><linearGradient id="g"><stop stop-color="#24AED3"/><stop offset=".52" stop-color="#697EC5"/><stop offset="1" stop-color="#D3488E"/></linearGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#E5EBF3" stroke-width=".65"/></pattern></defs><rect width="{width}" height="96" fill="#F7F9FC"/><rect x="{width-170}" width="170" height="96" fill="url(#grid)"/><path d="M0 95H{width}" stroke="#DBE2EC"/><path d="M0 28V68" stroke="#24AED3" stroke-width="6"/><text x="24" y="65" font-family="Arial,sans-serif" font-size="{size}" font-weight="900" font-style="italic" letter-spacing="-1" fill="url(#g)">{label}</text><path d="M{width-48} 48h20m-6-6 6 6-6 6" stroke="#24AED3" fill="none" stroke-width="2"/></svg>''')

# Genuine technology marks, kept locally with their licenses in design/icons.
import xml.etree.ElementTree as ET
ET.register_namespace('', 'http://www.w3.org/2000/svg')
logos=[('typescript','TypeScript'),('javascript','JavaScript'),('c','C'),('cpp','C++'),('java','Java'),('react','React'),('nextjs','Next.js'),('nodejs','Node.js'),('openai','OpenAI API'),('git','Git')]
for slug,label in logos:
 logo=ET.parse(ROOT/'design/icons'/f'{slug}.svg').getroot()
 logo.attrib.update(x='18',y='18',width='44',height='44')
 content=ET.tostring(logo,encoding='unicode')
 (OUT/f'{slug}.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80" role="img"><title>{label}</title><rect x=".5" y=".5" width="79" height="79" rx="16" fill="#F7F9FC" stroke="#E1E7EF"/>{content}</svg>''')

def create_mobile(scene=0):
 mobile=Image.new('RGB',(720,880),'#F5F8FC');d=ImageDraw.Draw(mobile)
 for x in range(0,720,24):d.line((x,0,x,880),fill='#E7EDF6')
 for y in range(0,880,24):d.line((0,y,720,y),fill='#E7EDF6')
 d.rectangle((32,39,62,45),fill=CYAN);d.rectangle((68,39,76,45),fill=PINK)
 tracked(d,(90,37),'ANCUO LOEWE',11,1.8,INK)
 text(d,(26,87),'WELCOME',96,bold=True,italic=True)
 gradient_text(mobile,(27,190),'TO MY WORLD.',79,width=636)
 panel=panel_for(scene,(650,490),True)
 mask=Image.new('L',(650,490));ImageDraw.Draw(mask).polygon([(28,0),(650,0),(620,490),(0,490)],fill=255)
 mobile.paste(panel,(35,321),mask);d=ImageDraw.Draw(mobile)
 d.line([(63,321),(685,321),(655,811),(35,811),(63,321)],fill='#97A9C1')
 d.polygon([(359,741),(694,741),(684,818),(349,818)],fill='#F9FBFD',outline=INK)
 d.line((360,755,356,777),fill=CYAN,width=4)
 text(d,(379,758),'NEVER STOP EXPLORING.',15,bold=True,italic=True)
 tracked(d,(379,785),f'0{scene+1} / 04',9,1.5)
 d.line((32,848,688,848),fill=LINE);d.rectangle((32,846,133,849),fill=CYAN)
 d.rectangle((645,846,686,849),fill=PINK)
 if scene==0: mobile.save(OUT/'hero-mobile.png',optimize=True)
 return mobile

carousel([create_mobile(i) for i in range(4)],OUT/'hero-mobile.webp',(720,880))

def button(filename,label,subtitle,dark=False):
 bg=INK if dark else '#F8FAFD';fg='#FFFFFF' if dark else INK
 (OUT/filename).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="250" height="52" viewBox="0 0 250 52" role="img"><title>{label}</title><path d="M.5.5H238L249.5 12V51.5H.5Z" fill="{bg}" stroke="{INK}"/><rect y="13" width="3" height="23" fill="{CYAN}"/><text x="17" y="24" fill="{fg}" font-family="Arial,sans-serif" font-size="12" font-weight="700">{label}</text><text x="17" y="39" fill="{'#BAC6D8' if dark else MUTED}" font-family="Arial,sans-serif" font-size="7" letter-spacing="1.3">{subtitle}</text><path d="m218 33 13-13m-12 0h12v12" fill="none" stroke="{CYAN}" stroke-width="1.7"/></svg>''')
button('explore.svg','EXPLORE REPOSITORIES','GITHUB / BLUEDINOSAUR233',True)
button('profile.svg','MEET ANCUO LOEWE','PERSONAL PROFILE')

print('Generated four-image carousels, three section headings, and technology logos.')
for name in ['hero.webp','hero-mobile.webp']:
 print(name,round((OUT/name).stat().st_size/1048576,2),'MB')
