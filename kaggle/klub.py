import re
from heapq import nlargest,nsmallest
from pprint import pprint

from text import get_stats,get_ngrams,get_prob

ROOT = '/home/mobarski/teksty/'
AUTHORS = ['ania','blake','felia','kamil','malgosia']

raw = {}
tokens = {}

for a in AUTHORS:
	text = open(ROOT+a+'.txt','r').read()
	raw[a] = text
	_tokens = re.findall('(?u)\w+',text)
	_tokens = [t for t in _tokens if t[0].lower()==t[0]] # bez nazw
	# TODO usuniecie koncowek
	# TODO usuniecie stopwords
	#_tokens = get_ngrams(_tokens,2)
	tokens[a] = _tokens

X = [tokens[a] for a in AUTHORS]
Y = range(len(AUTHORS))
model = get_stats(X,Y,base='tf',stats='wcp_y dia_y gini_y chi_y cmfs_y chi dia gini cmfs',treshold=20)
## print()
## for y in range(len(AUTHORS)):
	## print(AUTHORS[y],model['sum_y'][y])

## print()	
## for y in range(len(AUTHORS)):
	## print(AUTHORS[y])
	## pprint(model['tf_y'][y].most_common(10))

N = 50
print(' '*25,''.join(['{:<10}'.format(a) for a in AUTHORS]))
print()
words = nlargest(N,model['chi'].items(),key=lambda x:x[1]) # chi i dia sa sensowne
words = [w[0] for w in words]
for w,prob in get_prob(model,words,Y,'wcp_y'): # wcp lub tf jest sensowne
	line = ''.join(['{:20}'.format(w)]+['{:10.2f}'.format(p) for p in prob])
	print(line)

## print()	
## for y in range(len(AUTHORS)):
	## print(AUTHORS[y])
	## pprint(model['dia_y'][y].most_common(50))

# ==============================================================================

from itertools import chain
from collections import Counter
from random import choice
def markov(tokens):
	next_word = {}
	for t,n in zip(tokens,tokens[1:]):
		if t not in next_word: next_word[t] = Counter()
		next_word[t][n] += 1
	return next_word

if 0:
	print()
	m=markov(get_ngrams(tokens['malgosia'],1))
	w = choice([x for x in m if x[0].isupper()])
	for i in range(200):
		print(w.split(' ')[0],end=' ')
		choices = []
		for t,cnt in m[w].items():
			choices.extend([t]*cnt)
		w = choice(choices)
