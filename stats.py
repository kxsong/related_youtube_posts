import urlparse

httpscount = 0
features = {}

f = open('./urls-not-canonical.txt', 'r')
for line in f:
    p = urlparse.urlparse(line.rstrip())
    if p.scheme=='https':
        httpscount += 1
    query = urlparse.parse_qs(p.query)
    if query.has_key('feature'):
        if features.has_key(query['feature'][0]):
            features[query['feature'][0]] += 1
        else:
            features[query['feature'][0]] = 1
print features
print httpscount