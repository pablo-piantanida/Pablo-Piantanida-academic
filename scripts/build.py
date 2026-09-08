#!/usr/bin/env python3
"""Build the five-page static site from content, people/project data and BibTeX."""
from pathlib import Path
import html,json,re,shutil,os,unicodedata
import bibtexparser
from pylatexenc.latex2text import LatexNodes2Text
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'dist'; OUT.mkdir(exist_ok=True)
latex=LatexNodes2Text()
def clean(s):
    s=re.sub(r'\\(?:textcolor|colorbox)\{[^{}]*\}', '', s)
    s=latex.latex_to_text(s).replace('ﬁ','fi').replace('ﬂ','fl')
    return re.sub(r'\s+',' ',s).strip()
def esc(s):return html.escape(str(s),quote=True)
def read(name):return (ROOT/'content'/name).read_text()
def safe_url(u):
    u=u.strip().replace('\\&','&').replace('\\_','_').strip('{}')
    return u if u.startswith(('https://','http://')) else ''
def slug(s):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-')
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
nav=[('home','Home'),('research','Research'),('people','People'),('publications','Publications'),('projects','Projects')]
origin=os.environ.get('SITE_URL','').rstrip('/')
def page(name,title,body):
    pre='' if name=='home' else '../'
    links=''.join(f'<a href="{pre}{"" if key=="home" else key+"/"}"'+(' aria-current="page"' if key==name else '')+f'>{label}</a>' for key,label in nav)
    desc='Pablo Piantanida: mathematical foundations, evaluation and uncertainty, and adaptive collaborative AI. Full Professor and Director of ILLS, Montréal.'
    canonical=f'<link rel="canonical" href="{esc(origin)}/{"" if name=="home" else name+"/"}">' if origin else ''
    h=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Pablo Piantanida</title><meta name="description" content="{desc}">{canonical}<link rel="stylesheet" href="{pre}assets/style.css"><script defer src="{pre}assets/site.js"></script></head><body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="container"><div class="header-inner"><a class="brand" href="{pre or './'}">Pablo Piantanida</a><nav aria-label="Main navigation">{links}</nav></div></div></header><main id="main" class="container">{body}</main><footer class="site-footer"><div class="container footer-inner"><p>Pablo Piantanida<br>Montréal · Paris-Saclay</p><p><a href="mailto:pablo.piantanida@mila.quebec">Email</a> · <a href="https://orcid.org/0000-0002-8717-2117">ORCID</a> · <a href="{pre}assets/academic-cv.pdf">Academic CV</a><br>Updated September 2026</p></div></footer></body></html>'''
    dest=OUT if name=='home' else OUT/name;dest.mkdir(exist_ok=True);(dest/'index.html').write_text(h)
page('home','Mathematical foundations of reliable AI',read('home.html'))
page('research','Research',read('research.html'))
people=json.loads((ROOT/'data/people.json').read_text())
pbody=read('people-intro.html')
for group,label in [('current','Current doctoral researchers'),('alumni','Doctoral alumni'),('postdocs','Former postdoctoral fellows')]:
    pbody+=f'<section class="section"><h2>{label}</h2><div class="people-grid">'
    for x in people[group]:
        name=esc(x['name']); name=f'<a href="{esc(x["url"])}">{name}</a>' if x.get('url') else name
        pbody+=f'<article class="person"><h3>{name}</h3><p class="topic">{esc(x["topic"])}</p><p class="meta">{esc(x["institution"])}</p>'
        if x.get('coadvisors'):pbody+=f'<p class="small subtle">Co-supervision: {esc(x["coadvisors"])}</p>'
        if x.get('dates'):pbody+=f'<p class="small subtle">{esc(x["dates"])}</p>'
        pbody+='</article>'
    pbody+='</div></section>'
page('people','People',pbody+read('people-outro.html'))
projects=json.loads((ROOT/'data/projects.json').read_text()); projbody=read('projects-intro.html')
for group,label in [('active','Research programmes and collaborations'),('completed','Selected completed programmes')]:
    projbody+=f'<section class="section"><h2>{label}</h2>'
    for x in projects[group]:
        projbody+=f'<article class="project" id="{esc(x["id"])}"><div><p class="eyebrow">{esc(x["dates"])}</p><p class="meta">{esc(x["role"])}</p></div><div><h3>{esc(x["title"])}</h3><p class="meta">{esc(x["partners"])}</p><p>{esc(x["description"])}</p>'
        if x.get('url'):projbody+=f'<a href="{esc(x["url"])}">{esc(x.get("link_label","Project details"))}</a>'
        projbody+='</div></article>'
    projbody+='</section>'
page('projects','Projects and partnerships',projbody)
# Use precisely the active citation selection, rather than every legacy .bib entry.
selection=re.sub(r'(?<!\\)%[^\n]*','',(ROOT/'data/publication-selection.tex').read_text())
keys=list(dict.fromkeys(re.findall(r'\\bibentry\{([^}]+)\}',selection)))
entries={};raw=[]
for path in sorted((ROOT/'data').glob('*.bib')):
    text=path.read_text(); raw.append(text)
    for entry in bibtexparser.loads(text).entries:
        k=entry['ID']
        if k in entries and entries[k]!=entry:raise ValueError('Conflicting key '+k)
        entries[k]=entry
missing=[k for k in keys if k not in entries]
if missing:raise ValueError('Missing citation keys: '+str(missing))
records=[]; seen={};duplicate_keys=[]
for k in keys:
    e=entries[k];title=clean(e.get('title',''));doi=e.get('doi','').lower().strip()
    fingerprint=doi or slug(title)
    if fingerprint in seen:
        duplicate_keys.append({'key':k,'same_as':seen[fingerprint]});continue
    seen[fingerprint]=k
    yr=re.search(r'\d{4}',e.get('year',''));year=yr.group() if yr else 'Undated'
    typ='Journal' if e['ENTRYTYPE']=='article' and 'arxiv' not in e.get('journal','').lower() else 'Conference' if e['ENTRYTYPE']=='inproceedings' else 'Preprint / other'
    venue=clean(e.get('journal',e.get('booktitle',e.get('publisher',''))))
    # 2026 status copied from the CV is kept explicit; overrides can confirm publication later.
    override=json.loads((ROOT/'data/publication-overrides.json').read_text()).get(k,{})
    status=override.get('status','Venue listed in CV' if year=='2026' and typ in ('Journal','Conference') else '')
    authors='; '.join(clean(a) for a in re.split(r'\s+and\s+',e.get('author','')))
    links=[]
    if doi:links.append(('Paper','https://doi.org/'+doi))
    u=safe_url(e.get('url',''))
    if u:links.append(('arXiv' if 'arxiv.org/' in u else 'PDF' if '.pdf' in u else 'Paper',u))
    pdf=safe_url(e.get('pdf',''))
    if pdf:links.append(('PDF',pdf))
    ep=e.get('eprint','').strip()
    if ep and re.match(r'^\d{4}\.\d{4,5}(v\d+)?$',ep):links.append(('arXiv','https://arxiv.org/abs/'+ep))
    for u in re.findall(r'\\(?:href|url)\{([^}]+)\}',e.get('note','')):
        u=safe_url(u)
        if u:links.append(('arXiv' if 'arxiv.org/' in u else 'PDF' if '.pdf' in u else 'Paper',u))
    links=list(dict.fromkeys(links))
    records.append(dict(key=k,title=title,authors=authors,year=year,type=typ,venue=venue,status=status,links=links))
records.sort(key=lambda x:(x['year'],x['title']),reverse=True)
years=sorted({r['year'] for r in records},reverse=True)
body=read('publications-intro.html')
body+='<div class="pub-controls"><label>Search publications<input id="publication-search" type="search" placeholder="Title, author or keyword"></label><label>Year<select id="publication-year"><option value="">All years</option>'+''.join(f'<option>{y}</option>' for y in years)+'</select></label><label>Type<select id="publication-type"><option value="">All types</option><option>Journal</option><option>Conference</option><option>Preprint / other</option></select></label></div><p class="small subtle">Workshop papers and preprints are labelled in their bibliographic records. For recent entries, “venue listed in CV” indicates that publication status has not yet been independently confirmed.</p><p id="result-count" role="status" aria-live="polite"></p><p id="no-results" class="empty" hidden>No matching publications. Try another search or select all years and types.</p>'
for y in years:
    body+=f'<section class="year-group"><h2 class="year-heading">{y}</h2>'
    for r in [r for r in records if r['year']==y]:
        linked=f'<a href="{esc(r["links"][0][1])}">{esc(r["title"])}</a>' if r['links'] else esc(r['title'])
        body+=f'<article class="publication" id="{slug(r["key"])}" data-year="{r["year"]}" data-type="{r["type"]}"><h3>{linked}</h3><p class="small">{esc(r["authors"])}</p><p class="meta">{esc(r["venue"] or r["type"])} · {r["year"]}'+(f' · {esc(r["status"])}' if r['status'] else '')+'</p><div class="links">'+''.join(f'<a href="{esc(u)}">[{label}]</a>' for label,u in r['links'])+'</div></article>'
    body+='</section>'
page('publications','Publications',body)
writer=bibtexparser.bwriter.BibTexWriter(); db=bibtexparser.bibdatabase.BibDatabase(); db.entries=[entries[k] for k in keys];(OUT/'assets/publications.bib').write_text(writer.write(db))
(ROOT/'data/build-report.json').write_text(json.dumps({'selected_keys':len(keys),'displayed_records':len(records),'grouped_duplicates':duplicate_keys,'years':years,'recent_status_review':[r['key'] for r in records if r['status']]},indent=2))
(OUT/'.nojekyll').write_text('')
if origin:
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(origin)+'/'+('' if n=='home' else n+'/')+'</loc></url>' for n,_ in nav)+'</urlset>')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
else:(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print(f'Built five pages; {len(keys)} selected citations, {len(records)} displayed records.')
