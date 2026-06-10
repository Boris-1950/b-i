from html.parser import HTMLParser
text = open('bob.htm', encoding='utf-8').read()
class MyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
    def handle_starttag(self, tag, attrs):
        if tag in ['area','base','br','col','command','embed','hr','img','input','keygen','link','meta','param','source','track','wbr']:
            return
        self.stack.append((tag, self.getpos()))
    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f'Unmatched closing tag </{tag}> at {self.getpos()}')
            return
        last, pos = self.stack[-1]
        if last == tag:
            self.stack.pop()
            return
        self.errors.append(f'Expected </{last}> but found </{tag}> at {self.getpos()}')
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return
    def close(self):
        super().close()
        for tag, pos in self.stack:
            self.errors.append(f'Missing closing tag for <{tag}> opened at {pos}')
parser = MyParser()
parser.feed(text)
parser.close()
print('Errors:', len(parser.errors))
for err in parser.errors:
    print(err)
