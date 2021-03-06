from collections import Counter,defaultdict
from itertools import islice

# ==============================================================================

# TODO drop_under, drop_over, cut_low, cut_top
def get_stats(X, Y, base='df', stats='', agg='sum', norm='sum', alpha=0.5, merge=[], treshold=0):
	model = {}
	base_y = base+'_y'
	_stats = set(stats.split(' ')+[base,base_y,'p_y','sum_y'])
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

	for m in merge:
		model[base].update(m[base])
		for y in m[base_y]:
			model[base_y][y].update(m[base_y][y])
			_y.add(y)

	# drop terms below treshold
	if treshold:
		below = [t for t in model[base] if model[base][t]<=treshold]
		for t in below:
			del model[base][t]
			for y in _y:
				del model[base_y][y][t]

	for y in _y:
		model['sum_y'][y] = sum(model[base_y][y].values())

	if norm=='sum':
		_norm = sum(model[base].values())
		for y in _y:
			model['p_y'][y] = 1.0 * model['sum_y'][y] / _norm
	if norm=='doc':
		pass # TODO
	
	# ==[ local ]===========================================================
	
	if 'chi_y' in _stats:
		# TODO sum_f* vs base
		sum_f_y = {}
		for y in _y:
			sum_f_y[y] = sum(model[base_y][y].values())
		sum_f = sum(sum_f_y.values())
		for t,f in model[base].items():
			for y in _y:
				# observed
				o_c1_t1 = model[base_y][y][t]
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
				f_y = model[base_y][y].get(t,0)
				p_tc = 1.0 * f_y / cnt_y[y]
				p_ct = 1.0 * f_y / f
				model['cmfs_y'][y][t] = p_tc * p_ct
	
	if 'dia_y' in _stats:
		for t,f in model[base].items():
			for y in _y:
				f_y = model[base_y][y].get(t,0)
				p_ct = 1.0 * f_y / f
				model['dia_y'][y][t] = p_ct

	if 'diax_y' in _stats:
		for t,f in model[base].items():
			for y in _y:
				f_y = model[base_y][y].get(t,0)
				p_ct = 1.0 * f_y / f
				model['diax_y'][y][t] = p_ct/model['p_y'][y]

	if 'gini_y' in _stats:
		cnt_y = {}
		for y in _y:
			cnt_y[y] = Y.count(y) # TODO base=tf
		for t,f in model[base].items():
			for y in _y:
				f_y = model[base_y][y].get(t,0)
				p_tc = 1.0 * f_y / cnt_y[y]
				p_ct = 1.0 * f_y / f
				model['gini_y'][y][t] = p_tc*p_tc * p_ct*p_ct
	
	if 'wcp_y' in _stats:
		V = len(model[base])
		for y in _y:
			pr = {}
			for t in model[base]:
				f_y = model[base_y][y].get(t,0)
				pr[t] = (1.+f_y)/(V+model['sum_y'][y])
			_norm = sum(pr.values())
			for t in pr:
				model['wcp_y'][y][t] = pr[t]/_norm
	
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

def get_prob(model,tokens,Y,stat):
	out = []
	for t in tokens:
		norm = 0.0
		prob = []
		for y in Y:
			norm += model[stat][y][t]
		for y in Y:
			p = model[stat][y][t] / norm
			prob.append(p)
		out.append([t,prob])
	return out

# ==============================================================================

def get_ngrams(tokens, n, sep=' '):
    iters = [islice(tokens,i,None) for i in range(n)]
    return [sep.join(x) for x in zip(*iters)]

# ==============================================================================

if __name__=="__main__":
	X = ['xxx xxx ala ma kota','to jest test work ma','go go power ala ma','xxx xxx go work work kota ma']
	X = [x.split(' ') for x in X]
	Y = [0,1,1,0]
	m = get_stats(X,Y,'df','dia_y diax_y')
	#print(m['dia_y'][0])
	#print(m['dia'])
	#print(m['gini'])
	print(m['dia_y'][1])
	print(m['diax_y'][1])
	#print(get_ngrams('ala ma kota',2,''))
	#m2 = get_stats([['go','west'],['power','test']],[0,1],'df')
	#m3 = get_stats([],[],'df','dia_y',merge=[m,m2])
	#print(m3)
	
