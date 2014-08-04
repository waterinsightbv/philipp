import numpy as np
import pylab as pl
import pandas as pd

import os, sys
sys.path.append('wi')

from read_wispapp_file import read_avantes

data_dir = '/home/phil/Dropbox/shares/wisp-s_measurements/'

header = pd.DataFrame()
files = np.sort(os.listdir(data_dir))
for file in files[-5:]:
    header[file], angles, dark, data = read_avantes(data_dir + file)

header = header.T

print header