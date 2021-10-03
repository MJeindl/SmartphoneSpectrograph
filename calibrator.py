## Copyright (C) 2021 Jeindl
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

## Author: Maximilian Jeindl
version =  'Version 0.3.1 wip 16.08.2021'

import numpy as np
import tkinter as tk
import scipy.signal as sig
#WARNING! IF SOMETHING BREAKS IT MIGHT BE THE CALL FOR THIS MODULE
#todo
#IMPLEMENT CENTERING of data!!! very important
#also handover the centering
#find_peaks_cwt or find_peaks? find_peaks_cwt supposedly works more accurately with noise

#NotHappening
#include option for background substraction: for this use a slice of the picture again
#DECISION: background substraction is not going to be implemented due to the fact this can be easily achieved in post, by loading the background into excel etc, 
#another reason is the fact that the data format is going to become rather confusing and this would need bigger changes

#DONE
#calibration peak finder is broken, highest peak isn't displayed UPDATE: seems to work right now again, might be instable, pretty obvious when it happens so no concern of it screwing up data
#check if custom input is really consistent and works as it should UPDATE: linear is not working, array is being appended at the wrong side!
#consider introducing an automated error estimation -> doesn't really work with the low amount of data points usually used but will implement it anyways -> Covariance matrix is being printed, this should suffice for getting the data if you want it
#possibility to name the calibration

def wavFitReturn():
    global wavFit, indexOffset
    if 'wavFit' in globals():
        if len(wavFit) != 3:
            wavFit = np.array([0,1,0])
    else:
        wavFit = np.array([0,1,0])
    if 'indexOffset' in globals():
        'everything fine'
    else:
        indexOffset = int(0)

    return wavFit, indexOffset




#M Matrix either colour (x,y,3) or grayscale
#calibrator for pixel to wavelength
#not just having this grab a spectrum from the other monitor because I might just have it be able to show more than one spectrum, unlikely at the moment though
def calibrator(iPic, cPic):
    '''chucking this in here for the moment for troubleshooting, probably will stay here'''
    #have this check if the the data is already grayscale
    def summator(iPic, cPic):
        try:
            specdata = np.sum(iPic[cPic[0]:cPic[1]+1,:,:], axis = 2)
            specdata = np.sum(specdata, axis = 0)
        except:
            specdata = np.sum(iPic[cPic[0]:cPic[1]+1,:,:], axis = 0)
            print('alt spectralizer')
        #this does not norm right now, shouldn't be needed for the operation intended and can be done elsewhere
        return specdata

    #having these in here is inefficient but well, I need a solution for the moment; that might not be as temporary as I would like
    #will design this for a maximum of 10 peaks, don't think any more make sense
    def PeakFinder(spectraldata):
        #normalize for easier relative operation of manipulators
        spectraldata = spectraldata/np.max(spectraldata)
        #get data on how to find peaks
        if (len(ent_pwidth.get()) == 0) or (np.int(ent_pwidth.get()) == np.nan):
            pwidth = None
        else:
            pwidth = np.abs(np.int(ent_pwidth.get()))
        if (len(ent_pheight.get()) == 0) or (np.float32(ent_pheight.get()) == np.nan):
            pheight = None
        else:
            pheight = np.abs(np.float32(ent_pheight.get()))
        if (len(ent_pthresh.get()) == 0) or (np.float32(ent_pthresh.get()) == np.nan):
            pthresh = None
        else:
            pthresh = np.abs(np.float32(ent_pthresh.get()))

        ind, peakdict = sig.find_peaks(spectraldata, height = pheight, width = pwidth, distance = pthresh)
        #sort for heights, argsort gives indices for rising values
        sortind = np.argsort(-peakdict.get('peak_heights'))

        ind = ind[sortind]

        return ind




    def Peaker():
        specdata = summator(iPic, cPic)
        ind = PeakFinder(specdata)

        window_peak = tk.Tk()
        window_peak.title('Peak to wavelength')

        indtop = np.zeros((10))
    
        if len(ind)>10:
            indtop = ind[:10]
        else:
            indtop[:len(ind)] = ind[:]

        '''keeping this here to rebuild if needed
        for i in range(10):
            frame = tk.Frame(
                master = window_peak,
                width = 5,
                height = 2,
                bg = "lightgrey",
            )
            frame.grid(row=0, column = i)
            lbl_gen = tk.Label(frame, text = str(indtop[i]))
            lbl_gen.pack()
        '''
        #working for at least 2 input values
        #copied from below, to allow inputting specific pixel values for wavelength interpolation
        #type safety is not good, beware
        frameArrPx = []
        entArrPx = []
        for iterator in range(10):
            frameArrPx.append(tk.Frame(master = window_peak,
                width = 5,
                height = 2,
                bg = "lightgrey",))
            frameArrPx[iterator].grid(row = 1, column = iterator)
            entArrPx.append(tk.Entry(master = frameArrPx[iterator], 
                        width = 6,
                        fg = 'black',
                        bg = 'lightgrey'))
            #not sure if this is safe enough
            entArrPx[iterator].insert(0,str(int(indtop[iterator])))
            entArrPx[iterator].pack()
            

        #might be able to push this outside but it shouldn't matter much
        def pxToWav():
            #wavFit is to be a 3 element array for a second degree polynomial
            global wavFit, indexOffset
            wavs = np.zeros(10)
            #following lines new
            px = np.zeros(10)

            #this should work for time being, haven't checked it yet
            for iterator in range(10):
                wavs[iterator] = entArr[iterator].get()
                #following lines new
                px[iterator] = int(entArrPx[iterator].get())
                #sanitation
                if px[iterator] == np.nan:
                    wavs[iterator] = 0

            ##################################todo check function and handle handoff
            #check for number of valid inputs
            #indices = indtop[np.nonzero(wavs)] removed for variable input
            
            indices = px[np.nonzero(wavs)]
            
            indexOffset = int(np.mean(indices))
            print('Index Offset')
            print(indexOffset)
            
            #if to seperate 3 cases of too few inputs, 2 inputs and more than 2 inputs (maximum 2nd degree polynomial)
            if len(indices)<2:
                print('Not enough input parameters to calculate curve')
            elif len(indices) == 2:
                temp = np.polyfit(indices-indexOffset, wavs[np.nonzero(wavs)], deg = 1)
                wavFit = np.zeros(3)
                #this should be the right way [a,b,c] corresponds to a x^2 +b x + c
                wavFit[1:] = temp[:]
            elif len(indices) == 3:
                wavFit = np.polyfit(indices-indexOffset, wavs[np.nonzero(wavs)], deg = 2)
            else:
                wavFit, covariance = np.polyfit(indices-indexOffset, wavs[np.nonzero(wavs)], deg = 2, cov = True)
                print('Covariance')
                print(covariance)
            

                
            print('Polynomial coefficients')
            print(wavFit)
            

        #rebuild of this section done
        frameArr = []
        entArr = []
        for iterator in range(10):
            frameArr.append(tk.Frame(master = window_peak,
                width = 5,
                height = 2,
                bg = "lightgrey",))
            frameArr[iterator].grid(row = 2, column = iterator)
            entArr.append(tk.Entry(master = frameArr[iterator], 
                        width = 6,
                        fg = 'black',
                        bg = 'lightgrey'))
            entArr[iterator].insert(0,str(0))
            entArr[iterator].pack()




        #####Button for calculation
        btnArr = []
        btn_pxToWav = tk.Button(
            text = "Pixel-To-Wavelength",
            master = window_peak,
            #master = frameR,
            command = pxToWav,
            width = 18,
            height = 3,
            bg = "lightgrey",
            fg = "black",
            relief = tk.GROOVE
            )
        btnArr.append(btn_pxToWav)
        btnArr[0].grid(row = 0, column = 0, columnspan=3, sticky = tk.W+tk.E)

        btnArr.append(tk.Label(
            master = window_peak, 
            text = 'Name: ', 
            width = 6,
            height = 3))
        btnArr[1].grid(row = 0, column = 4)

        btnArr.append(tk.Entry( 
            master = window_peak,
            width = 18,
            fg = 'black',
            bg = 'lightgrey'))
        btnArr[2].grid(row=0, column = 5, columnspan= 3,sticky = tk.W+tk.E)
    	
        global CalibName
        CalibName = btnArr[2]

        tk.mainloop()
        

        return ind





    window_cal = tk.Tk()
    window_cal.title('Spectra Calibration')

    frameL = tk.Frame(
        master = window_cal,
        relief = tk.RAISED,
        borderwidth = 1
    )
    frameL.grid(row=0, column=0)

    frameR = tk.Frame(
        master = window_cal,
        relief = tk.RAISED,
        borderwidth = 1
    )
    frameR.grid(row=0,column=1)

    btn_peaks = tk.Button(
        text = "find peaks",
        master = frameL,
        command = Peaker,
        width = 12,
        height = 3,
        bg = "lightgrey",
        fg = "black",
        relief = tk.GROOVE
        )
    btn_peaks.pack()


    lbl_pwidth = tk.Label(
        master = frameL,
        text = 'minimum width of peaks'
    )
    ent_pwidth = tk.Entry(
        master = frameL,
        width = 6,
        fg = 'black',
        bg = 'lightgrey'
    )
    lbl_pwidth.pack()
    ent_pwidth.pack()

    lbl_pheight = tk.Label(
        master = frameL,
        text = 'minimum rel. height of peaks'
    )
    ent_pheight = tk.Entry(
        master = frameL,
        width = 6,
        fg = 'black',
        bg = 'lightgrey'
    )
    lbl_pheight.pack()
    ent_pheight.insert(0, str(0.1))
    ent_pheight.pack()
    
    #this here is used with the distance option of find_peaks
    lbl_pthresh = tk.Label(
        master = frameL,
        text = 'Distance'
    )
    ent_pthresh = tk.Entry(
        master = frameL,
        width = 6,
        fg = 'black',
        bg = 'lightgrey'
    )
    lbl_pthresh.pack()
    ent_pthresh.pack()



    tk.mainloop()

#if this works I am keeping it UPDATE: keeping it
def CalibNameReturn():
    try: 
        calibname = CalibName.get()
        return calibname
    except:
        #return blank
        return str(' ')