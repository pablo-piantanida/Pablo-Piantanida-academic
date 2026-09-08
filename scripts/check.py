from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
root=Path(__file__).resolve().parents[1]/'dist'
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=[];self.h1=0
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if 'id' in a:self.ids.append(a['id'])
  for k in ('href','src'):
   if a.get(k):self.refs.append(a[k])
errors=[];pages=list(root.rglob('*.html'));parsed={}
for p in pages:
 parser=Parser();parser.feed(p.read_text());parsed[p]=parser
 if parser.h1!=1:errors.append(f'{p}: expected one h1')
 if len(parser.ids)!=len(set(parser.ids)):errors.append(f'{p}: duplicate ids')
for p,parser in parsed.items():
 for ref in parser.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  dest=(p.parent/unquote(u.path)).resolve() if u.path else p
  if dest.is_dir():dest=dest/'index.html'
  if not dest.exists():errors.append(f'{p.name}: missing {ref}')
  if u.fragment and dest in parsed and u.fragment not in parsed[dest].ids:errors.append(f'{p.name}: missing anchor {ref}')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} HTML pages; local links, assets, anchors, heading counts and unique ids.')
