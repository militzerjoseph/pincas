"""Keep the classic icon designer and add the user-approved picture launcher."""
from pathlib import Path
import base64, json, re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parent
res=root/'app/src/main/res/drawable-nodpi'
for encoded in root.rglob('*.webp.b64'):
    encoded.with_suffix('').write_bytes(base64.b64decode(encoded.read_text()))
    encoded.unlink()
html=(root/'app/src/main/assets/index.html').read_text()
raw=re.search(r'let ICON_BACKGROUND_OPTIONS=(\[.*?\]);',html).group(1)
bgs=json.loads(re.sub(r'(?<=[{,])(id|label|color):',r'"\1":',raw))
colors={'white':'#FFFFFF','black':'#111111','charcoal':'#333333','navy':'#17305E','yellow':'#FFD86E'}
fonts=[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')]
fontpath=next((p for p in fonts if p.exists()),None)
if fontpath is None: raise RuntimeError('Install DejaVu Sans or Arial to generate classic Hebrew icons')
A='{http://schemas.android.com/apk/res/android}'
ET.register_namespace('android',A[1:-1]);p=root/'app/src/main/AndroidManifest.xml';tree=ET.parse(p);app=tree.getroot().find('application')
for old in app.findall('activity-alias'):app.remove(old)
def alias(name,icon,enabled=False):
    e=ET.SubElement(app,'activity-alias',{A+'name':'.'+name,A+'targetActivity':'.MainActivity',A+'exported':'true',A+'enabled':str(enabled).lower(),A+'icon':'@drawable/'+icon,A+'roundIcon':'@drawable/'+icon})
    f=ET.SubElement(e,'intent-filter');ET.SubElement(f,'action',{A+'name':'android.intent.action.MAIN'});ET.SubElement(f,'category',{A+'name':'android.intent.category.LAUNCHER'})
alias('Picture','ic_launcher',True)
for bg in bgs:
    for grid in (False,True):
        for size,pt in [('small',72),('normal',88),('large',105)]:
            for color,ink in colors.items():
                name='text_'+bg['id']+'_'+('grid' if grid else 'plain')+'_'+size+'_'+color
                im=Image.new('RGBA',(432,432));d=ImageDraw.Draw(im);d.rounded_rectangle((0,0,431,431),radius=76,fill=bg['color'])
                if grid:
                    layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer)
                    for n in range(0,432,43):ld.line((n,0,n,432),fill=(255,255,255,90),width=2);ld.line((0,n,432,n),fill=(255,255,255,90),width=2)
                    layer.putalpha(Image.composite(layer.getchannel('A'),Image.new('L',im.size,0),im.getchannel('A')));im=Image.alpha_composite(im,layer);d=ImageDraw.Draw(im)
                font=ImageFont.truetype(str(fontpath),pt);d.text((216,216),'בנקים',font=font,fill=ink,anchor='mm',direction='rtl')
                im.save(res/(name+'.png'));alias('Text_'+name[5:],name)
tree.write(p,encoding='unicode',xml_declaration=True)
print('Prepared approved icon and',len(bgs)*2*3*5,'classic icon choices')
