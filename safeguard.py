import re
from detoxify import Detoxify

model = Detoxify('original-small')

banned_vocabulary = [
    r'\bn[i1!]gg[ae]r?\b',
    r'\bk[i1!]k[e3]?\b',
    r'\bch[i1!]nk\b',
    r'\bs[p5]ic\b',
    r'\bf[a4]g(got)?\b',
    r'\bd[y1!]ke\b',
    r'\btr[a4]nn[y1!]?\b',
    r'\bret[a4]rd(ed)?\b',
    r'\bm[o0]ng\b',
    r'\bcr[a4]ck[e3]r\b',
    r'\bj[e3]w\b',
    r'\bn[a4]z[i1!]\b',
    r'\bsl[u]t\b',
    r'\bc[u]nt\b',
    r'\bp[u]ssy\b',
    r'\bc[o0]ck\b',
    r'\bd[i1!]ck\b',
    r'\bwh[o0]re\b',
    r'\bf[u]ck(er|ing)?\b',
    r'\bsh[i1!]t\b',
    r'\b[a@]ss(h[o0]le)?\b',
    r'\bb[i1!]tch\b',
    r'\bc[u]m\b',
    r'\bbl[o0]wj[o0]b\b',
    r'\bcl[i1!]t\b',
    r'\bc[o0]nd[o0]m\b',
    r'\bs[u]ck my\b',
    r'\bp[e3]nis\b',
    r'\bv[a4]gina\b',
    r'\bgangbang\b',
    r'\br[a4]pe\b',
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
