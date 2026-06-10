from html.parser import HTMLParser
from collections import defaultdict
import re
path='bob.htm'
text=open(path, encoding='utf-8').read()
void_tags={'area','base','br','col','command','embed','hr','img','input','keygen','link','meta','param','source','track','wbr'}
class MyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.errors=[]
        self.counts=defaultdict(int)
        self.lastpos=None
    def handle_starttag(self, tag, attrs):
        self.counts[tag]+=1
        self.lastpos=self.getpos()
        if tag in void_tags:
            return
        self.stack.append((tag,self.getpos()))
    def handle_endtag(self, tag):
        self.counts[tag]+=1
        self.lastpos=self.getpos()
        if not self.stack:
            self.errors.append(f'Unmatched closing </{tag}> at {self.getpos()}')
            return
        last,pos=self.stack[-1]
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
parser=MyParser()
parser.feed(text)
parser.close()
print('Error count:', len(parser.errors))
for err in parser.errors:
    print(err)
print('---')
print('Stack remaining:', len(parser.stack))
print('Section opens/closes:', parser.counts['section'])
print('Main opens/closes:', parser.counts['main'])
print('Nav opens/closes:', parser.counts['nav'])
print('Body opens/closes:', parser.counts['body'])
print('HTML opens/closes:', parser.counts['html'])
# find any raw ampersands not part of entities in text
bad_ampersands = [m.start() for m in re.finditer(r'&(?!(?:nbsp|lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);)', text)]
print('Bad ampersands:', len(bad_ampersands))
if bad_ampersands:
    for pos in bad_ampersands[:20]:
        print('pos',pos, text[pos-20:pos+20].replace('\n',' '))
