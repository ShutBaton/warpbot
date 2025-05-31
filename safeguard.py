import re
from detoxify import Detoxify

model = Detoxify('original-small')

banned_vocabulary = [
    r'n[i1!]gg[ae]r?',
    r'k[i1!]k[e3]?',
    r'ch[i1!]nk',
    r's[p5]ic',
    r'f[a4]g(got)?',
    r'd[y1!]ke',
    r'tr[a4]nn[y1!]?',
    r'ret[a4]rd(ed)?',
    r'm[o0]ng',
    r'cr[a4]ck[e3]r',
    r'j[e3]w',
    r'n[a4]z[i1!]',
    r'sl[u]t',
    r'c[u]nt',
    r'p[u]ssy',
    r'c[o0]ck',
    r'd[i1!]ck',
    r'wh[o0]re',
    r'f[u]ck(er|ing)?',
    r'sh[i1!]t',
    r'[a@]ss(h[o0]le)?',
    r'b[i1!]tch',
    r'c[u]m',
    r'bl[o0]wj[o0]b',
    r'cl[i1!]t',
    r'c[o0]nd[o0]m',
    r's[u]ck my',
    r'p[e3]nis',
    r'v[a4]gina',
    r'gangbang',
    r'r[a4]pe',
]

def keyword_match(text: str) -> bool:
    for pattern in banned_vocabulary:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def is_toxic(text: str, threshold: float = 0.7) -> bool:
    results = model.predict(text)
    return any(score >= threshold for score in results.values())

def scan_content(text: str) -> bool:
    return is_toxic(text) or keyword_match(text)
