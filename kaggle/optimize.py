from __future__ import print_function
from time import time
from multiprocessing import Pool

def train_test_split(X,Y,test_size=0.2,sample=1.0):
	from random import random
	x_train,y_train,x_test,y_test = [],[],[],[]
	for x,y in zip(X,Y):
		if sample<1 and random()>sample: continue
		if random()<test_size:
			x_test.append(x)
			y_test.append(y)
		else:
			x_train.append(x)
			y_train.append(y)
	return x_train,y_train,x_test,y_test


def flat_search(X,Y,args,
		train_fun,
		predict_fun,
		score_fun,
		repeat=3,
		test_size=0.2,
		sample=1.0,
		workers=1,
		verbose=0):
	n_runs = repeat * sum([len(x) for x in args.values()])
	print('RUNS:',n_runs) if verbose else None
	out = {} # out[arg][val] -> [scores...]
	# TODO workers
	i = 0
	for _ in range(repeat):
		x_train,y_train,x_test,y_test = train_test_split(X,Y,test_size,sample)
		for k,vals in args.items():
			if k not in out: out[k] = {}
			v_orig = globals().get(k)
			for v in vals:
				i += 1
				if v not in out[k]: out[k][v] = []
				globals()[k]=v
				t0 = time()
				model = train_fun(x_train,y_train)
				pred = predict_fun(model,x_test)
				score = score_fun(y_test,pred)
				dt = time()-t0
				out[k][v] += [score]
				#print('RUN {} / {} COMPLETE  {} = {}'.format(i,n_runs,k,v)) if verbose else None
				print('RUN {} / {} COMPLETE  {}'.format(i,n_runs,'  '.join(['{}:{}'.format(_k,_v) for _k,_v in globals().items() if type(_v) in (int,float)]))) if verbose else None
			globals()[k] = v_orig # TODO pick best 
	return out

if __name__=="__main__":
	TOP = 9
	NGRAM = 9
	def train(*args): return {}
	def predict(*args): return []
	def score(*args): return 0.42
	out = flat_search([],[],
		dict(TOP=[1,2,3,4,5,6,7,8],NGRAM=[1,2,3,4]),
		train,predict,score,
		repeat=3,verbose=1)
	print(out)
	print(train_test_split([1,2,3,4,5,6,7,8,9,10],[0,0,0,0,0,1,1,1,1,1],test_size=0.4))
	
