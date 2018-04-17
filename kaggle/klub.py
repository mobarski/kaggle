import re
from heapq import nlargest,nsmallest

from text import get_stats,get_ngrams

ROOT = '/home/mobarski/teksty/'
AUTHORS = ['ania','blake','felia','kamil','malgosia']

raw = {}
tokens = {}

for a in AUTHORS:
	text = open(ROOT+a+'.txt','r').read()
	raw[a] = text
	_tokens = re.findall('(?u)\w+',text)
	#_tokens = [t for t in _tokens if t[0].lower()==t[0]] # bez nazw
	# TODO usuniecie koncowek
	# TODO usuniecie stopwords
	#_tokens = get_ngrams(_tokens,2)
	tokens[a] = _tokens

X = [tokens[a] for a in AUTHORS]
Y = range(len(AUTHORS))
model = get_stats(X,Y,base='tf',stats='wcp_y dia_y gini_y chi_y cmfs_y',treshold=1)

print()
for y in range(len(AUTHORS)):
	print(AUTHORS[y],model['sum_y'][y])

print()	
for y in range(len(AUTHORS)):
	print(AUTHORS[y],model['tf_y'][y].most_common(10))

print()	
for y in range(len(AUTHORS)):
	print(AUTHORS[y],model['dia_y'][y].most_common(50))

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

print()
m=markov(get_ngrams(tokens['blake'],2)+get_ngrams(tokens['felia'],2))
w = choice([x for x in m if x[0].isupper()])
for i in range(100):
	print(w.split(' ')[0],end=' ')
	choices = []
	for t,cnt in m[w].items():
		choices.extend([t]*cnt)
	w = choice(choices)
