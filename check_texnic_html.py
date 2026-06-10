from html.parser import HTMLParser
import re
path = 'texnic.htm'
text = open(path, encoding='utf-8').read()
void_tags = {'area','base','br','col','command','embed','hr','img','input','keygen','link','meta','param','source','track','wbr'}
class MyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.errors=[]
        self.counts={}
    def handle_starttag(self, tag, attrs):
        self.counts[tag] = self.counts.get(tag,0)+1
        if tag not in void_tags:
            self.stack.append((tag,self.getpos()))
    def handle_endtag(self, tag):
        self.counts[tag] = self.counts.get(tag,0)+1
        if not self.stack:
            self.errors.append(f'Unmatched closing </{tag}> at {self.getpos()}')
            return
        last,pos = self.stack[-1]
        if last==tag:
            self.stack.pop()
            return
        self.errors.append(f'Expected </{last}> but found </{tag}> at {self.getpos()}')
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]
                return
    def close(self):
        super().close()
        for tag,pos in self.stack:
            self.errors.append(f'Missing closing </{tag}> opened at {pos}')
parser = MyParser()
parser.feed(text)
parser.close()
print('ERRORS', len(parser.errors))
for e in parser.errors:
    print(e)
print('---')
print('counts:', parser.counts)
bad_amps = [m.start() for m in re.finditer(r'&(?!(?:nbsp|lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);)', text)]
print('bad_amp_count', len(bad_amps))
for pos in bad_amps[:20]:
    print(pos, repr(text[max(0,pos-20):pos+20]))
