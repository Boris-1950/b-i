import os, re
root = os.getcwd()
files = []
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if fn.lower().endswith(('.htm','.html')):
            files.append(os.path.join(dirpath, fn))
rawamp = re.compile(r'&(?!(?:nbsp|lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')
for fp in files:
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    raw = list(rawamp.finditer(text))
    a_open = [m for m in re.finditer(r'<a\b', text, flags=re.I)]
    a_close = [m for m in re.finditer(r'</a>', text, flags=re.I)]
    xCompat = len(re.findall(r'<meta\s+http-equiv="X-UA-Compatible"', text, flags=re.I))
    viewport = len(re.findall(r'<meta\s+name="viewport"', text, flags=re.I))
    if raw or len(a_open) != len(a_close) or xCompat>1 or viewport>1:
        print('FILE:', os.path.relpath(fp, root))
        print('  raw_amp:', len(raw), 'a_open:', len(a_open), 'a_close:', len(a_close), 'x_compat:', xCompat, 'viewport:', viewport)
        if raw:
            for m in raw[:10]:
                line = text.count('\n',0,m.start())+1
                snippet = text[max(0,m.start()-20):m.end()+20].replace('\n',' ')
                print(f'    raw {line}: {snippet}')
        if len(a_open) != len(a_close):
            print('    a_open examples:')
            for m in a_open[:5]:
                line = text.count('\n',0,m.start())+1
                snippet = text[max(0,m.start()-20):m.end()+60].replace('\n',' ')
                print(f'      open {line}: {snippet}')
            print('    a_close examples:')
            for m in a_close[:5]:
                line = text.count('\n',0,m.start())+1
                snippet = text[max(0,m.start()-20):m.end()+20].replace('\n',' ')
                print(f'      close {line}: {snippet}')
        if xCompat>1 or viewport>1:
            print('    meta duplicates in head?')
        print()
