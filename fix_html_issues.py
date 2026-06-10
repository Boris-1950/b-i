import os
import re

root = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(root, 'fix_html_issues.log')
after_path = os.path.join(root, 'fix_html_after_report.txt')
report_path = os.path.join(root, 'html_report_current.txt')

raw_amp = re.compile(r'&(?![A-Za-z]+;|#\d+;|#x[0-9A-Fa-f]+;)')
meta_x = re.compile(r'(<meta\b[^>]*http-equiv=["\']X-UA-Compatible["\'][^>]*>)', re.I)
meta_v = re.compile(r'(<meta\b[^>]*name=["\']viewport["\'][^>]*>)', re.I)
a_open = re.compile(r'<a\b', re.I)
a_close = re.compile(r'</a>', re.I)


def balance_anchor_tags(text):
    tokens = []
    for m in a_open.finditer(text):
        tokens.append(('open', m.start(), m.end()))
    for m in a_close.finditer(text):
        tokens.append(('close', m.start(), m.end()))
    tokens.sort(key=lambda x: x[1])
    stack = []
    unmatched_closes = []
    for typ, start, end in tokens:
        if typ == 'open':
            stack.append((start, end))
        else:
            if stack:
                stack.pop()
            else:
                unmatched_closes.append((start, end))
    if not unmatched_closes and not stack:
        return text, 0, 0
    if unmatched_closes:
        new_text = []
        last = 0
        for start, end in unmatched_closes:
            new_text.append(text[last:start])
            last = end
        new_text.append(text[last:])
        text = ''.join(new_text)
    if stack:
        text = text + '</a>' * len(stack)
    return text, len(stack), len(unmatched_closes)

html_files = []
for dirpath, dirnames, filenames in os.walk(root):
    for filename in filenames:
        if filename.lower().endswith(('.htm', '.html')):
            html_files.append(os.path.join(dirpath, filename))
html_files.sort()

with open(log_path, 'w', encoding='utf-8') as log, open(report_path, 'w', encoding='utf-8') as report:
    log.write('fix_html_issues started\n')
    report.write('FILE,raw_amp,a_open,a_close,X-UA-Compatible,viewport,anchor_open,anchor_close,unmatched_open,unmatched_close,changed\n')
    for path in html_files:
        rel = os.path.relpath(path, root)
        text = open(path, 'r', encoding='utf-8', errors='replace').read()
        changed = False
        changed_details = []

        amp_matches = raw_amp.findall(text)
        if amp_matches:
            text = raw_amp.sub('&amp;', text)
            changed = True
            changed_details.append(f'raw_amp={len(amp_matches)}')

        x_matches = list(meta_x.finditer(text))
        if len(x_matches) > 1:
            remove_spans = [m.span() for m in x_matches[1:]]
            new_text = []
            last_index = 0
            for start, end in remove_spans:
                new_text.append(text[last_index:start])
                last_index = end
            new_text.append(text[last_index:])
            text = ''.join(new_text)
            changed = True
            changed_details.append(f'X-UA-Compatible removed={len(x_matches)-1}')

        v_matches = list(meta_v.finditer(text))
        if len(v_matches) > 1:
            remove_spans = [m.span() for m in v_matches[1:]]
            new_text = []
            last_index = 0
            for start, end in remove_spans:
                new_text.append(text[last_index:start])
                last_index = end
            new_text.append(text[last_index:])
            text = ''.join(new_text)
            changed = True
            changed_details.append(f'viewport removed={len(v_matches)-1}')

        anchor_open_count = len(a_open.findall(text))
        anchor_close_count = len(a_close.findall(text))
        text, unmatched_open, unmatched_close = balance_anchor_tags(text)
        if unmatched_open or unmatched_close:
            changed = True
            if unmatched_open:
                changed_details.append(f'unmatched_open_appended={unmatched_open}')
            if unmatched_close:
                changed_details.append(f'unmatched_close_removed={unmatched_close}')
            anchor_open_count = len(a_open.findall(text))
            anchor_close_count = len(a_close.findall(text))

        if changed:
            with open(path, 'w', encoding='utf-8', newline='') as out:
                out.write(text)
            log.write(f"FIXED {rel}: {'; '.join(changed_details)}\n")
        else:
            log.write(f'NO CHANGE {rel}\n')

        report.write(','.join([
            rel,
            str(len(amp_matches)),
            str(anchor_open_count),
            str(anchor_close_count),
            str(len(x_matches)),
            str(len(v_matches)),
            str(anchor_open_count),
            str(anchor_close_count),
            str(unmatched_open),
            str(unmatched_close),
            'yes' if changed else 'no'
        ]) + '\n')

    log.write('DONE\n')

with open(after_path, 'w', encoding='utf-8') as out:
    out.write('after fix verification\n')
    for path in html_files:
        rel = os.path.relpath(path, root)
        text = open(path, 'r', encoding='utf-8', errors='replace').read()
        out.write(f"{rel} raw_amp={len(raw_amp.findall(text))} X-UA-Compatible={len(meta_x.findall(text))} viewport={len(meta_v.findall(text))} a_open={len(a_open.findall(text))} a_close={len(a_close.findall(text))}\n")
