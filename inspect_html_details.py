import os, re
root = os.getcwd()
files = [
'avn/dvm/ogl_dvm.htm',
'avn/armi_polit.htm',
'avn/kachestvo.htm',
'avn/okr_ru.htm',
'avn/p_p.htm',
'galaxy/galactik (3).htm',
'gkg/g3.htm',
'041170.htm'
]
rawamp = re.compile(r'&(?!(?:nbsp|lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')
for rel in files:
    fp = os.path.join(root, rel)
    if not os.path.exists(fp):
        print('MISSING', rel)
        continue
    text = open(fp, 'r', encoding='utf-8', errors='replace').read()
    raw = list(rawamp.finditer(text))
    opens = list(re.finditer(r'<a\b', text, flags=re.I))
    closes = list(re.finditer(r'</a>', text, flags=re.I))
    print('FILE', rel)
    print(' raw_amp', len(raw), 'opens', len(opens), 'closes', len(closes))
    if raw:
        for m in raw[:10]:
            line = text.count('\n', 0, m.start()) + 1
            print('   RAW', line, repr(text[max(0, m.start()-30):m.start()+30]))
    if len(opens) != len(closes):
        for m in opens[:10]:
            line = text.count('\n', 0, m.start()) + 1
            print('   OPEN', line, repr(text[m.start():m.start()+120]))
        for m in closes[:10]:
            line = text.count('\n', 0, m.start()) + 1
            print('   CLOSE', line, repr(text[m.start():m.start()+20]))
    print()
