from pathlib import Path
import re

path = Path('bob.htm')
text = path.read_text(encoding='utf-8')

# Find all <p ...>...</p> blocks (including those spanning multiple lines)
blocks = []
for m in re.finditer(r'<p[^>]*>(.*?)</p>', text, flags=re.DOTALL | re.IGNORECASE):
    inner = m.group(1)
    # remove any inner HTML tags and normalize whitespace
    clean = re.sub(r'<[^>]+>', '', inner)
    clean = re.sub(r'\s+', ' ', clean).strip()
    lineno = text.count('\n', 0, m.start()) + 1
    blocks.append((lineno, clean))

seen = {}
for idx, (lineno, clean) in enumerate(blocks):
    if len(clean) < 30:
        continue
    seen.setdefault(clean, []).append(lineno)

dups = {k: v for k, v in seen.items() if len(v) > 1}
if not dups:
    print('No duplicate paragraph blocks found')
else:
    for i, (text_snip, lines) in enumerate(dups.items(), start=1):
        print(f'Duplicate #{i}: occurs {len(lines)} times at lines {lines}')
        print('  Snippet:', text_snip[:200])
