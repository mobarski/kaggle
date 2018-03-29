from collections import Counter,defaultdict
from itertools import islice

# ==============================================================================

def get_stats(X, Y, base='df', stats='', agg='sum', norm='sum', alpha=0.5):
	model = {}
	_stats = set(stats.split(' ')+[base,base+'_y'])
	_y = set(Y)
	
	for s in _stats:
		if s.endswith('_y'):
			model[s] = defaultdict(Counter)
		else:
			model[s] = Counter()
	
	# ==[ base ]============================================================
	
	for tokens,y in zip(X,Y):
		if 'tf' in _stats:
			tf = Counter(tokens)
			model['tf_y'][y].update(tf)
			model['tf'].update(tf)
		
		if 'df' in _stats:
			df = Counter(set(tokens))
			model['df_y'][y].update(df)
			model['df'].update(df)

	pass # TODO drop terms below treshold


	# ==[ local ]===========================================================
	
	if 'chi_y' in _stats:
		# TODO sum_f* vs base
		sum_f_y = {}
		for y in _y:
			sum_f_y[y] = sum(model[base+'_y'][y].values())
		sum_f = sum(sum_f_y.values())
		for t,f in model[base].items():
			for y in _y:
				# observed
				o_c1_t1 = model[base+'_y'][y][t]
				o_c1_t0 = sum_f_y[y] - o_c1_t1
				o_c0_t1 = model[base][t] - o_c1_t1
				o_c0_t0 = sum_f-sum_f_y[y] - o_c0_t1
				# expected
				e_c1_t1 = 1.0 * o_c0_t1 / (sum_f-sum_f_y[y]) * sum_f_y[y]
				e_c1_t0 = 1.0 * o_c0_t0 / (sum_f-sum_f_y[y]) * sum_f_y[y] # ???
				e_c0_t1 = 1.0 * o_c1_t1 / sum_f_y[y] * (sum_f-sum_f_y[y])
				e_c0_t0 = 1.0 * o_c1_t0 / sum_f_y[y] * (sum_f-sum_f_y[y]) # ???
				# components
				c1_t1 = (o_c1_t1 - e_c1_t1)**2 / (e_c1_t1 + alpha)
				c1_t0 = (o_c1_t0 - e_c1_t0)**2 / (e_c1_t0 + alpha)
				c0_t1 = (o_c0_t1 - e_c0_t1)**2 / (e_c0_t1 + alpha)
				c0_t0 = (o_c0_t0 - e_c0_t0)**2 / (e_c0_t0 + alpha)
				model['chi_y'][y][t] = c0_t0+c1_t0+c0_t1+c1_t1
	
	if 'cmfs_y' in _stats:
		cnt_y = {}
		for y in _y:
			cnt_y[y] = Y.count(y) # TODO base=tf
		for t,f in model[base].items():
			for y in _y:
				f_y = model[base+'_y'][y].get(t,0)
				p_tc = 1.0 * f_y / cnt_y[y]
				p_ct = 1.0 * f_y / f
				model['cmfs_y'][y][t] = p_tc * p_ct
	
	if 'dia_y' in _stats:
		for t,f in model[base].items():
			for y in _y:
				f_y = model[base+'_y'][y].get(t,0)
				p_ct = 1.0 * f_y / f
				model['dia_y'][y][t] = p_ct

	if 'gini_y' in _stats:
		cnt_y = {}
		for y in _y:
			cnt_y[y] = Y.count(y) # TODO base=tf
		for t,f in model[base].items():
			for y in _y:
				f_y = model[base+'_y'][y].get(t,0)
				p_tc = 1.0 * f_y / cnt_y[y]
				p_ct = 1.0 * f_y / f
				model['gini_y'][y][t] = p_tc*p_tc * p_ct*p_ct
	
	if 'wcp_y' in _stats:
		pass # TODO
	
	
	# TODO - my functions 
	
	# TODO *x_y - ballanced variants


	# ==[ global ]==========================================================

	if 'chi' in _stats:
		for t in model[base]:
			scores = [model['chi_y'][y][t] for y in _y]
			model['chi'][t] = max(scores) # TODO agg
		
	if 'cmfs' in _stats:
		for t in model[base]:
			scores = [model['cmfs_y'][y][t] for y in _y]
			model['cmfs'][t] = max(scores) # TODO agg

	if 'dia' in _stats:
		for t in model[base]:
			scores = [model['dia_y'][y][t] for y in _y]
			model['dia'][t] = max(scores) # agg=sum always==1

	if 'gini' in _stats:
		for t in model[base]:
			scores = [model['gini_y'][y][t] for y in _y]
			model['gini'][t] = sum(scores) # always sum

	
	return model

# ==============================================================================

def get_ngrams(tokens, n, sep=' '):
    iters = [islice(tokens,i,None) for i in range(n)]
    return [sep.join(x) for x in zip(*iters)]


if __name__=="__main__":
	X = ['xxx xxx ala ma kota','to jest test work ma','go go power ala ma','xxx xxx go work work kota ma']
	X = [x.split(' ') for x in X]
	Y = [0,1,1,0]
	m = get_stats(X,Y,'df','chi_y chi')
	#print(m['dia_y'][0])
	#print(m['dia'])
	#print(m['gini'])
	print(m['chi'])
	#print(get_ngrams('ala ma kota',2,''))
