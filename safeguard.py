import re
from detoxify import Detoxify

model = Detoxify('original-small')

banned_vocabulary = [
    r'(?<!\w)n[i1!]gg[ae]r?(?!\w)',
    r'(?<!\w)k[i1!]k[e3]?(?!\w)',
    r'(?<!\w)ch[i1!]nk(?!\w)',
    r'(?<!\w)s[p5]ic(?!\w)',
    r'(?<!\w)f[a4]g(got)?(?!\w)',
    r'(?<!\w)d[y1!]ke(?!\w)',
    r'(?<!\w)tr[a4]nn[y1!]?(?!\w)',
    r'(?<!\w)ret[a4]rd(ed)?(?!\w)',
    r'(?<!\w)m[o0]ng(?!\w)',
    r'(?<!\w)cr[a4]ck[e3]r(?!\w)',
    r'(?<!\w)j[e3]w(?!\w)',
    r'(?<!\w)n[a4]z[i1!](?!\w)',
    r'(?<!\w)sl[u]t(?!\w)',
    r'(?<!\w)c[u]nt(?!\w)',
    r'(?<!\w)p[u]ssy(?!\w)',
    r'(?<!\w)c[o0]ck(?!\w)',
    r'(?<!\w)d[i1!]ck(?!\w)',
    r'(?<!\w)wh[o0]re(?!\w)',
    r'(?<!\w)f[u]ck(er|ing)?(?!\w)',
    r'(?<!\w)sh[i1!]t(?!\w)',
    r'(?<!\w)[a@]ss(h[o0]le)?(?!\w)',
    r'(?<!\w)b[i1!]tch(?!\w)',
    r'(?<!\w)c[u]m(?!\w)',
    r'(?<!\w)bl[o0]wj[o0]b(?!\w)',
    r'(?<!\w)cl[i1!]t(?!\w)',
    r'(?<!\w)c[o0]nd[o0]m(?!\w)',
    r'(?<!\w)s[u]ck my(?!\w)',
    r'(?<!\w)p[e3]nis(?!\w)',
    r'(?<!\w)v[a4]gina(?!\w)',
    r'(?<!\w)gangbang(?!\w)',
    r'(?<!\w)r[a4]pe(?!\w)',
]

def keyword_match(text: str) -> bool:
    for pattern in banned_vocabulary:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def text_scan(text: str, threshold: float = 0.8) -> bool:
    results = model.predict(text)
    return any(score >= threshold for score in results.values())

def scan_content(text: str) -> bool:
    return text_scan(text) or keyword_match(text)

if __name__ == '__main__':
    text_input = input("Enter content to scan: ")
    print(f"Harmful content found = {str(scan_content(text_input))}")
