import numpy as np
import pylab as pl
import pandas as pd
import glob
import os, sys
from time import time

def read_avantes(file, dark_correction = True):
    header = pd.read_csv(file, header=1, sep=': ', nrows=9).iloc[:,0]
    header.name = 'Metadata'

    tmp = pd.read_csv(file, header=12, sep=',', index_col=0)

    angles = tmp.iloc[:6]
    angles.index.name = 'Angle'

    dark = tmp.iloc[8:26]
    dark.index.name = 'DarkPixel'

    data = tmp.iloc[28:]
    data = data.astype(np.int32)
    data.index = np.asarray(data.index,dtype=np.float32)
    data.index.name = 'Wavelength, [nm]'    
    data.columns.name = 'Measurement, [#]'

    # The DLL uses the first 14 darkpixels: in deadpix array nr 2 to 15, so deadpix 0, 1, 16, 17 are not used at all. From these 14 pixels, the pixels with highest and lowest odd and even intensity are also not used. The intensity for the remaining 5 odd pixels are averaged and subtracted from all odd datapixels (1, 3, 5, ...2047) The intensity for the remaining 5 even pixels are averaged and subtracted from all even datapixels (0, 2 4, ..2046)

    tmp = dark[2:16]
    odd = tmp[1::2]
    even = tmp[::2]

    odd = odd[(odd != odd.max()) & (odd != odd.min())].mean()
    even = even[(even != even.max()) & (even != even.min())].mean()
    
    dark.loc['odd'] = odd
    dark.loc['even'] = even
    
    if dark_correction == True:
        even = data.iloc[::2] - even
        odd = data.iloc[1::2] - odd

        data = pd.concat((even,odd)).sort()
        

    return header, angles, dark, data

def plot_spectral_scan(d, title='', xlabel='Wavelength, [nm]', ylabel='Measurement Number, [#]', zlabel='Digital Counts, [#]', lims = 'percentile', limval=5, cmap='jet', interpolation='None', figsize = (8,10), new_figure = True, clf = True, savefig = False, showfig = True):
    
    if new_figure == True:
        pl.figure(figsize=figsize)
    else:
        pl.figure(0, figsize=figsize)
        if clf == True:
            pl.clf()

    if lims == 'fixed':
        vmin = limval[0]
        vmax = limval[1]
    elif lims == 'percentile':
        vmin = np.percentile(d.values, limval)
        vmax = np.percentile(d.values, 100 - limval)
    else:
        raise Exception('lims: fixed or percentile')

    pl.imshow(d.T, aspect='auto', extent=(d.index[0], d.index[-1], 1, d.shape[1]), origin='lower', cmap=cmap, interpolation=interpolation)

    pl.title(title)
    
    cbar = pl.colorbar(fraction=0.05, pad = 0.01, use_gridspec=True)
    
    cbar.ax.set_ylabel(zlabel)
        
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
        
    pl.grid()

    pl.tight_layout()
    
    def saveFigure(filename):        
        dir = os.path.split(filename)[0]
        if not os.path.exists(dir):
            os.makedirs(dir)

        pl.savefig(filename)

    if type(savefig) == str:    
        saveFigure(savefig)
    elif type(savefig) == tuple:
        for filename in savefig:
            saveFigure(filename)

    if showfig == True:
        pl.show()
    else: pl.close()


if __name__ == '__main__':
    data_dir = '/home/phil/Dropbox/shares/wisp-s_measurements/'

    files = np.sort(os.listdir(data_dir))

    header, angles, dark, data = read_avantes(data_dir + files[-1], dark_correction=True)
    #header, angles, data = read_avantes(data_dir + 'measurement_20140722_105939.txt')


    print header

    data.plot()
    pl.title('Spectra')
    pl.ylabel('Counts, [#]')
    pl.show()

    '''
    #angles.T.plot()    
    angle_labels = ('Roll', 'Azimuth', 'Pitch')
    colors = ('r', 'g', 'b')
    pl.figure()
    for i in range(3):
        pl.plot(range(angles.shape[1]), angles[i::3].mean(), colors[i], label=angle_labels[i])
        pl.quiver(range(angles.shape[1]), angles[i::3].mean(), np.zeros(angles.shape[1]), angles[i::3].diff().iloc[1], scale=200, width=0.005, color=colors[i])
    pl.title('Angles')
    pl.legend(loc=0)
    pl.grid()
    pl.ylabel('Angle, [deg]')
    pl.xlabel('Measurement, [#]')
    pl.show()    


    plot_spectral_scan(data)
    '''