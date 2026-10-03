from collections import Counter
from html.parser import HTMLParser
import math
import re
import unicodedata

import experiment as base

STOP_WORDS = set('a ao aos as co con da das de del do dos e el en es este esta o os la las lo los no non na nas nos nun para pola por que se un unha una y the is of in to for'.split())


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocked = []
        self.in_body = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True
        if tag in ('script', 'style', 'noscript', 'nav', 'header', 'footer', 'form', 'svg', 'head'):
            self.blocked.append(tag)

    def handle_endtag(self, tag):
        if self.blocked and tag == self.blocked[-1]:
            self.blocked.pop()
        if tag == 'body':
            self.in_body = False

    def handle_data(self, data):
        if self.in_body and not self.blocked:
            self.parts.append(data)


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))


def tokens(text):
    return [word for word in re.findall(r'[a-z0-9]+', normalize(text)) if len(word) > 1 and word not in STOP_WORDS]


def windows(text, size=120, overlap=30):
    words = text.split()
    for start in range(0, len(words), size-overlap):
        excerpt = ' '.join(words[start:start+size])
        if excerpt:
            yield excerpt
        if start+size >= len(words):
            break


def document_pages(path):
    if path.suffix == '.pdf':
        from pypdf import PdfReader
        return [(f'PDF p. {i}', page.extract_text() or '') for i, page in enumerate(PdfReader(path).pages, 1)]
    parser = VisibleHTML()
    parser.feed(path.read_text(encoding='utf-8', errors='replace'))
    return [('HTML body; automatic text extraction', ' '.join(parser.parts))]


def build_corpus(sources):
    chunks = []
    counts = {}
    for source in sources:
        pages = document_pages(base.ROOT / source['snapshot'])
        counts[source['sourceId']] = len(pages)
        for page_number, (locator, text) in enumerate(pages, 1):
            for index, excerpt in enumerate(windows(text), 1):
                chunk = {key: source.get(key) for key in ['title', 'url', 'documentDate', 'referencePeriod', 'kind', 'phase', 'unit', 'attribution', 'dependencyGroup']}
                chunk.update(sourceId=f"{source['sourceId']}-p{page_number:03}-c{index:03}",
                    documentId=source['sourceId'], locator=f'{locator}; window {index}', excerpt=excerpt,
                    snapshotSha256=source['snapshotSha256'])
                chunks.append(chunk)
    return dict(chunks=chunks, documentPageCounts=counts, method='all PDF pages and cleaned HTML body; 120 words with 30-word overlap; no reference passages used')


def retrieve(query, chunks, limit=6, per_document=2):
    documents = [tokens(c['excerpt']+' '+c['title']) for c in chunks]
    frequencies = Counter(token for document in documents for token in set(document))
    average = sum(map(len, documents))/len(documents) if documents else 1
    query_tokens = set(tokens(query))
    ranking = []
    for chunk, document in zip(chunks, documents):
        counts = Counter(document)
        score = 0.0
        for token in query_tokens:
            count = counts[token]
            if count:
                inverse = math.log(1+(len(chunks)-frequencies[token]+.5)/(frequencies[token]+.5))
                score += inverse*count*2.5/(count+1.5*(.25+.75*len(document)/average))
        if score > 0:
            ranking.append((score, chunk))
    ranking.sort(key=lambda pair: (-pair[0], pair[1]['sourceId']))
    selected = []
    document_counts = Counter()
    for score, chunk in ranking:
        if document_counts[chunk['documentId']] >= per_document:
            continue
        selected.append(dict(chunk, retrievalScore=round(score, 6)))
        document_counts[chunk['documentId']] += 1
        if len(selected) == limit:
            break
    return selected
