import numpy as np
import pylab as pl
import pandas as pd
import glob
import os, sys
import subprocess

sys.path.append('wi')
from read_wispapp_file import read_avantes

data_dir = '/home/phil/Dropbox/shares/wisp-s_measurements/'
files = np.sort(os.listdir(data_dir))



def read(it, nrscans=1):
	
	try:
		subprocess.call('wi/avantes_connect/measure %1.2f %i' % (it, nrscans), stdout=open(os.devnull, 'w'), shell=True)
	except: raise ValueError

	files = np.sort(os.listdir(data_dir))
	# print files[-1]

	header, angles, dark, data = read_avantes(data_dir + files[-1], dark_correction=False)
	
	return data

def smart_it(verbose=True):
	val_max = 2**16. - 1
	it = 2
	data = read(it)

	if data.max().max() == val_max:
		if verbose == True: print 'Lower IT limit reached, too much light!'
		return -1

	it = 50
	data = read(it)
	if data.max().max() == val_max:
		if verbose == True: print 'Lowering IT...'
		while data.max().max() == val_max:
			it = it / 5.
			if verbose == True: print it
			
			if it < 2.:
				it = 2				
				if verbose == True: print 'Lower IT limit reached, too much light!'
				return -1

			data = read(it)

	if verbose == True: print 'Increasing IT...'
	while ((val_max * 0.95) / data.max().max()) > 1.05:
		it = (val_max) / data.max().max() * it
		
		data = read(it)
		if verbose == True: print 'IT: %1.2f ms, %1.2f %% of optimum' % (it, (data.max().max() / (val_max * 0.95)) * 100)
	if verbose == True: print 'Optimal IT: %1.2f ms' % it

	return int(np.round(it))

if __name__ == '__main__':
	it = smart_it()

		