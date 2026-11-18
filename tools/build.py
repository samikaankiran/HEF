import re,os,sys,json,shutil
sys.path.insert(0,os.path.dirname(__file__))
from tr import TR,pattern
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,'..','_src')   # English originals
OUT=os.path.join(HERE,'..')
PAGES=['index','about','projects','contact','privacy','cookies','data-protection']
BASE='https://www.hef.com.tr'
missing=set()
def tr_str(s):
    if s in TR: return TR[s]
    p=pattern(s)
    if p: return p
    return None
def translate_text(seg):
    # seg: raw text between tags (may contain entities)
    parts=re.split(r'(&[#a-zA-Z0-9]+;)',seg)
    out=[]
    for p in parts:
        if p.startswith('&') and p.endswith(';'): out.append(p); continue
        st=p.strip()
        if not st or not re.search('[A-Za-z]',st): out.append(p); continue
        t=tr_str(st)
        if t is None: missing.add(st); out.append(p); continue
        lead=p[:len(p)-len(p.lstrip())]; trail=p[len(p.rstrip()):]
        out.append(lead+t+trail)
    return ''.join(out)
ATTR_RE=re.compile(r'\b(alt|aria-label|title|placeholder|content)="([^"]*)"')
def translate_tag(tag):
    def r(m):
        v=m[2]; t=tr_str(v)
        if t is None:
            if m[1]!='content' and re.search('[A-Za-z]{3}',v) and not v.startswith('http'): missing.add('@'+v)
            return m[0]
        return f'{m[1]}="{t}"'
    return ATTR_RE.sub(r,tag)
def translate_html(html):
    toks=re.split(r'(<[^>]+>)',html); depth=0; out=[]
    for t in toks:
        if t.startswith('<'):
            low=t.lower()
            if re.match(r'<(script|style|svg)\b',low): out.append(t if depth else translate_tag(t)); depth+=1; continue
            if re.match(r'</(script|style|svg)>',low): depth-=1; out.append(t); continue
            out.append(t if depth else translate_tag(t))
        else:
            out.append(t if depth else translate_text(t))
    return ''.join(out)
def h1_tr(html):
    m=re.search(r'(<h1 id="h-hero"[^>]*>)(.*?)(</h1>)',html,re.S)
    if not m: return html
    words=['Işık,','malzeme,','oran.']; d=700; parts=[]
    for w in words:
        s=''
        for ch in w: s+=f'<span class="tw" style="--d:{d}ms">{ch}</span>'; d+=55
        parts.append(s)
    inner='<span aria-hidden="true">'+'<br>'.join(parts)+'</span>'
    return html[:m.start(2)]+inner+html[m.end(2):]
def page_url(lang,pg): return f'{BASE}/{lang}/' + ('' if pg=='index' else pg+'.html')
def common(html,lang,pg):
    other='tr' if lang=='en' else 'en'
    html=re.sub(r'<html lang="[a-z]+">',f'<html lang="{lang}">',html,1)
    html=re.sub(r'(href|src)="assets/',r'\1="/assets/',html)
    if pg!='404':
        url=page_url(lang,pg)
        html=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="{url}">\n<link rel="alternate" hreflang="tr" href="{page_url("tr",pg)}">\n<link rel="alternate" hreflang="en" href="{page_url("en",pg)}">\n<link rel="alternate" hreflang="x-default" href="{page_url("tr",pg)}">',html,1)
        html=re.sub(r'<meta property="og:url" content="[^"]*">',f'<meta property="og:url" content="{url}">\n<meta property="og:locale" content="{"tr_TR" if lang=="tr" else "en_US"}">',html,1)
    # language switch in header nav
    target=(f'/{other}/' + ('' if pg in('index','404') else pg+'.html'))
    label='EN' if other=='en' else 'TR'; name='English' if other=='en' else 'Türkçe'
    li=f'<li><a class="lang" href="{target}" hreflang="{other}" lang="{other}" aria-label="{name}">{label}</a></li>\n      '
    html=html.replace('<nav class="site-nav" aria-label="Main menu">\n    <ul>\n      ','<nav class="site-nav" aria-label="Main menu">\n    <ul>\n      '+li,1)
    assert 'class="lang"' in html, pg
    css='.site-nav a.lang{transition:opacity 300ms var(--ease);opacity:.65}.site-nav a.lang:hover,.site-nav a.lang:focus-visible{opacity:1}\n'
    html=html.replace('</style>',css+'</style>',1)
    return html
def tr_extra(html):
    html=html.replace("n+(n===1?' project':' projects')","n+' proje'")
    html=html.replace("'Open image: '","'Görseli aç: '").replace("'Image gallery'","'Görsel galerisi'")
    html=html.replace('type="button">Close</button>','type="button">Kapat</button>')
    html=html.replace('aria-label="Previous image"','aria-label="Önceki görsel"').replace('aria-label="Next image"','aria-label="Sonraki görsel"')
    html=html.replace('data-map-title="HEF office location on Google Maps"','data-map-title="Google Haritalar’da HEF ofisinin konumu"').replace('&amp;hl=en&amp;','&amp;hl=tr&amp;')
    return html
for lang in ('en','tr'):
    os.makedirs(f'{OUT}/{lang}',exist_ok=True)
    for pg in PAGES:
        h=open(f'{SRC}/{pg}.html',encoding='utf-8').read()
        h=common(h,lang,pg)
        if lang=='tr':
            h=h1_tr(h); h=translate_html(h); h=tr_extra(h)
        open(f'{OUT}/{lang}/{pg}.html','w',encoding='utf-8').write(h)
# root 404: Turkish, absolute links into /tr/
h=open(f'{SRC}/404.html',encoding='utf-8').read()
h=common(h,'tr','404')
h=re.sub(r'href="/((?:about|projects|contact|privacy|cookies|data-protection)\.html[^"]*)"',r'href="/tr/\1"',h)
h=h.replace('href="/"','href="/tr/"')
h=translate_html(h); h=tr_extra(h)
open(f'{OUT}/404.html','w',encoding='utf-8').write(h)
print('missing:',json.dumps(sorted(missing),ensure_ascii=False,indent=0))
