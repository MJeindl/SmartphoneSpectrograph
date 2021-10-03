import numpy as np
import scipy.signal as sig
import tkinter as tk
import tkinter.filedialog
import scipy.optimize as sopt
import matplotlib.pyplot as plt


filename = tkinter.filedialog.askopenfilename(
        filetypes = [('All Files', '*.*')]
    )
data = np.loadtxt(filename, comments = '#', delimiter=';', usecols = [1,2])

#use known polynomial
pol = [3.49552085e-06, 3.27763385e-01, 5.27560261e+02]
indexOffset = 2450
id = 5
rel_height = 0.1

ind, inf = sig.find_peaks(data[:,1], height = rel_height*max(data[:,1]), width=1, distance = 4, prominence=0.4, rel_height=0.5)
print('indizes')
print(ind)
print('wavelength')
print(data[ind,0])
print('id')
print(id)
print('id wavelength')
print(data[ind[id],0])
#uses prominence height, might need to change that
print('FWHM-direct data')
print(inf['widths'])



def fitfunc(x, sigma, mu, s):
    return s*np.exp(-(x-mu)**2/(2*sigma**2))


xrange = range(ind[id]-int(inf['widths'][id]), ind[id]+int(inf['widths'][id]))
popt, pcov = sopt.curve_fit(fitfunc, xrange, data[xrange, 1], p0 = [0.5, int(ind[id]), data[ind[id],1]], bounds=([0, -np.inf, -np.inf], np.inf))
print(popt)

print('FWHM-Fit')
fwhm = (2*np.sqrt(2*np.log(2))*popt[0])
print(str(fwhm))



plt.figure()
plt.plot(xrange, data[xrange,1], label ='data')
xplotrange=np.linspace(ind[id]-int(inf['widths'][id]), ind[id]+int(inf['widths'][id]), num = 100)
plt.plot(xplotrange, fitfunc(xplotrange, popt[0], popt[1], popt[2]), label = 'fit')
plt.legend()
plt.show()



popt = popt - indexOffset
#wavelength fwhm = tfwhm = abs(wave(pos+fwhm/2)-wav(pos -fwhm/2))
fwhmPos = np.polyval(pol,[popt[1]-fwhm/2, popt[1]+fwhm/2])
tfwhm = abs(fwhmPos[1]-fwhmPos[0])

print('wavelength fwhm / nm')
print(str(tfwhm))
print('spectral resolution, delta lambda = tfwhm/2')
print((2*data[ind[id],0])/tfwhm)