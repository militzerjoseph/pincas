from pathlib import Path

# Reuse the proven BTL V8 icon pipeline, but render the color icons with the Hebrew label 'כספים'.
code=Path('btl_icon_style_v8.py').read_text(encoding='utf-8')
old="code = code.replace('מניות', 'ב.לאומי')"
new="code = code.replace('מניות', 'כספים')"
if old not in code:
    raise SystemExit('Could not patch BTL V8 label replacement')
code=code.replace(old,new,1)
exec(compile(code,'ksafim-v8-color-style','exec'),{})
print('Ksafim V8 color icons rendered with label כספים')
