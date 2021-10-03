## Copyright (C) 2021 Maximilian Jeindl
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

## Author: Maximilian Jeindl
version =  'Version 0.3.1 wip 16.08.2021'
#from BachelorProject.calibrator import all
import tkinter as tk
import numpy as np 
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from PIL import Image
from numpy.core.defchararray import index
import calibrator as calib



#todo
#make matplotlib windows dynamically change size, no clue how, would also need to make fonts dynamically change but that isn't going to happen
#consider importing calibration settings

#######
#optional
#save exif, might not be feasible with the tools I have
#######
#done
#show the imported file name
#swapped jpeg to be the first option


#global array for input picture is iPic, cut picture coordinates is cPic=(top cutoff, bottom cutoff)
#global array for 

def calibrate():
    #open new window for calibration
    #window_cal = tk.Tk()
    #window_cal.title('Spectra Calibration')
    calib.calibrator(iPic, cPic)

#######################################
#have this as specinput so I don't have to necessarily rewrite specdata when trying to show something else
#waveinput may be left empty to just get the pixel correlation
def redrawSpec(specInput,waveinput=[]):
    if len(waveinput) == 0:
        waveinput = range(np.shape(iPic)[1])
    figSpec.clear()
    figSpec.add_subplot(111).plot(waveinput, specInput)
    figSpec.suptitle(str(specPath), fontsize = 10)
    canvasSpec.draw()

def spectralizer():
    global specdata
    global normBool
    global specPath
    normBool = False
    #get the line values
    #works now, dunno if try except is needed
    try:
        specdata = np.sum(iPic[cPic[0]:cPic[1]+1,:,:], axis = 2)
        specdata = np.sum(specdata, axis = 0)
    except:
        specdata = np.sum(iPic[cPic[0]:cPic[1]+1,:,:], axis = 0)
        print('alt spectralizer')

    specPath = filepathIn
    redrawSpec(specdata)


def normSwitch():
    global normBool
    '''introduce wavelength later on'''
    if normBool == False:
        redrawSpec(specdata/np.max(specdata))
        normBool = True
    else:
        redrawSpec(specdata)
        normBool = False

#this here basically switches the x axis from pixels to wavelength
def WavShow():
    global indexOffset
    wavFit, indexOffset = calib.wavFitReturn()
    #not necessarily efficient, might have to put a global variable later as that shape never changes
    waveinput = np.polyval(wavFit, np.arange(0,np.shape(iPic)[1],1)-indexOffset)
    redrawSpec(specdata, waveinput)

#not nice but for the moment
enterStr = '''
'''
csvHeader = ['''order is [px position, wavelength equivalent, summed value], 
wavelength calculation is done with polynomial: 
''', 
'''
index-offset is: ''',
'''
From the picturefile lines used are: 
''',
'''
Calibration-name: ''']

#working good enough for now, could certainly be done in a nicer way but works
def specSave():
    global specdata
    global indexOffset
    filepathInputSpec = tk.filedialog.asksaveasfilename(
        filetypes = [('TXT', '*.txt'), ('All Files', '*.*')]
    )
    pxVector = np.arange(0, np.shape(iPic)[1],1)
    wavPol, indexOffset = calib.wavFitReturn()
    
    #check for right dimensions, should be done now with cPic
    #the wavelength still is in the right order, just the indices used to calculate it isn't
    data = np.transpose([pxVector, np.polyval(wavPol, pxVector-indexOffset),specdata])

    CalibName = calib.CalibNameReturn()
    if len(CalibName) > 0:
        #print('first case')
        header_str = str(version + enterStr + csvHeader[0] + str(wavPol) + csvHeader[1] + str(indexOffset) + csvHeader[2]+ str(cPic) + csvHeader[3] + str(CalibName))
    else:
        header_str = str(version + enterStr + csvHeader[0] + str(wavPol) + csvHeader[1] + str(indexOffset) + csvHeader[2]+ str(cPic))
    np.savetxt(filepathInputSpec, data, delimiter=';', header=header_str, comments = '#')
    
    

    
#######################################

def saveCut():
    #open save window
    filepathCut = tk.filedialog.asksaveasfilename(
        filetypes = [('PNG', '*.png'), ('All Files', '*.*')]
        )
    if not filepathCut:
        return
    #trying if it works better with PIL which I hope
    '''
    try:
        plt.figure()
        plt.imshow(iPic[cPic[0]:cPic[1],:,:])
        plt.savefig(filepathCut, transparent=False)
        plt.close()
    except:
        try:
            plt.figure()
            plt.imshow(iPic[cPic[0]:cPic[1],:])
            plt.savefig(filepathCut,transparent=False)
            plt.close()
        except:
            'do nothing'
            '''
    try:
        imCut = Image.fromarray(iPic[cPic[0]:cPic[1]+1,:,:])
        imCut.save(filepathCut)
    except:
        try:
            imCut = Image.fromarray(iPic[cPic[0]:cPic[1]+1,:])
            imCut.save(filepathCut)
        except: 'do nothing'

def openiPic():
    global filepathIn
    filepathInputPic = tk.filedialog.askopenfilename(
        filetypes = [('JPG', '*.jpg'), ('PNG', '*.png'),  ('All Files', '*.*')]
    )
    if not filepathInputPic:
        return
    #shorten filepath for display
    pathstr = filepathInputPic.split('/')
    filepathIn = '/'.join(pathstr[-2::1])

    global iPic 
    iPic = np.array(Image.open(filepathInputPic))[:,:,:3]
    redrawPic(iPic)

#to centralize this
def redrawPic(iPic):
    figPic.clear()
    figPic.add_subplot(111).imshow(iPic)
    figPic.suptitle(str(filepathIn), fontsize = 10)
    canvasPic.draw()

    
def rotate():
    global iPic
    iPic = np.rot90(iPic)
    redrawPic(iPic)

def cut():
    global iPic
    global cPic
    
    cPic = np.ndarray((2), dtype = int)
    try:
        size = np.size(iPic[:,0,0])
    except:
        size = np.size(iPic[:,0])
    cPic[0] = int(ent_upperLim.get())
    #to include the last pixel
    cPic[1] = int(ent_lowerLim.get())
    if cPic[0] < 0:
        cPic[0] = 0
    if cPic[1] < 0:
        cPic[1] = 0


    if cPic[0] > cPic[1]:
        temp = cPic[0]
        cPic[0] = cPic[1]
        cPic[1] = temp
    elif cPic[0] == cPic[1]:
        cPic[0] = 0
        cPic[1] = size
    
    #include chosen pixel row, beware it starts counting at zero UPDATE: was already solved where it was used
    #cPic[1] += 1

    if cPic[1] > size:
        cPic[1] = size
    #oh god, this is basically unreadable, it does insert 4 white lines in the picture before the cutoff values
    
    
    if isinstance(iPic[0,0,0], np.float32):
        #might be broken, but don't know yet, might be float64 or similar, should never happen though as uint8 is standard for PIL afaik
        maxval = float(1)
    elif isinstance(iPic[0,0,0], np.uint8):
        maxval = np.uint8(255)
    else:
        print('Alt Picture Format')
        print(type(iPic[0,0,0]))
    temp = np.zeros((np.shape(iPic)[0]+8, np.shape(iPic)[1], np.shape(iPic)[2]), dtype = type(iPic[0,0,0]))
    temp[0:cPic[0],:,:]= iPic[0:cPic[0],:,:]
    temp[cPic[0]:cPic[0]+4, :,:] = maxval
    temp[(cPic[0]+4):cPic[1]+4,:,:]= iPic[cPic[0]:cPic[1],:,:]
    temp[cPic[1]+4:cPic[1]+8, :,:] = maxval
    temp[cPic[1]+8:, :, :] = iPic[cPic[1]:,:,:]

    redrawPic(temp)
    
    
    
    

    








########################################################
window = tk.Tk()


window.columnconfigure([0], weight = 1, minsize = 100)
window.columnconfigure([1], weight = 2, minsize = 100)
window.rowconfigure([0,1], weight = 1, minsize = 100)

window.title('Spectra Evaluator')
#left top picture controll
frame0 = tk.Frame(
    master = window,
    relief = tk.RAISED,
    borderwidth = 1
    )
frame0.grid(row=0, column=0)

#input picture controll layout
btn_rot = tk.Button(
    text = "rot90",
    master = frame0,
    command = rotate,
    width = 12,
    height = 3,
    bg = "lightgrey",
    fg = "black",
    relief = tk.GROOVE
    )
btn_rot.pack()

lbl_upperLim = tk.Label(
    master = frame0,
    text = 'upper boundary incl.'
)
ent_upperLim = tk.Entry(
    master = frame0,
    width = 6,
    fg = 'black',
    bg = 'lightgrey'
)
lbl_upperLim.pack()
ent_upperLim.pack()

lbl_lowerLim = tk.Label(
    master = frame0,
    text = 'lower boundary incl.'
)
ent_lowerLim = tk.Entry(
    master = frame0,
    width = 6,
    fg = 'black',
    bg = 'lightgrey'
)
lbl_lowerLim.pack()
ent_lowerLim.pack()
##############################################
#load and save

bttn_loadInputPic = tk.Button(
    master = frame0,
    command = openiPic,
    fg = 'black',
    bg = 'lightgrey',
    width = 12,
    height = 3,
    text = 'Load Picture',
    relief = tk.GROOVE
    )
bttn_loadInputPic.pack()

bttn_Cut = tk.Button(
    master = frame0,
    command = cut,
    fg = 'black',
    bg = 'lightgrey',
    width = 12,
    height = 3,
    text = 'Cut Picture',
    relief = tk.GROOVE
)
bttn_Cut.pack()

bttn_saveCut = tk.Button(
    master = frame0,
    command = saveCut,
    fg = 'black',
    bg = 'lightgrey',
    width = 12,
    height = 3,
    text = 'Save Cut Picture',
    relief = tk.GROOVE
)
bttn_saveCut.pack()
##############################################
#Plot picture top right

frame1 = tk.Frame(
    master = window,
    relief = tk.RAISED,
    borderwidth = 1
    )
frame1.grid(row=0, column=1)


figPic = Figure(dpi = 100)
try:
    figPic.add_subplot(111).imshow(iPic)
except:
    #clear is needed because in the future it won't just overwrite with add_subplot but make a new instance
    figPic.clear()
    figPic.add_subplot(111).plot(cmap = 'gray', norm ='normalize', interpolation='none')

canvasPic = FigureCanvasTkAgg(figPic, master = frame1)
canvasPic.draw()
toolbar = NavigationToolbar2Tk(canvasPic, frame1)
toolbar.update()
canvasPic.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand = 1)

##############################################
#other buttons for saving and stuff

frame2 = tk.Frame(
    master = window,
    relief = tk.RAISED,
    borderwidth = 1
    )
frame2.grid(row=1, column=0)

bttn_saveSpec = tk.Button(
    master = frame2,
    command = specSave,
    fg = 'black',
    bg = 'lightgrey',
    width = 10,
    height = 3,
    text = 'Save Spectra',
    relief = tk.GROOVE
)
bttn_saveSpec.pack()

bttn_cal = tk.Button(
    master = frame2,
    command = calibrate,
    fg = 'black',
    bg = 'lightgrey',
    width = 10,
    height = 3,
    text = 'Calibration',
    relief = tk.GROOVE
)
bttn_cal.pack()

bttn_normspec = tk.Button(
    master = frame2,
    command = normSwitch,
    fg = 'black',
    bg = 'lightgrey',
    width = 10,
    height = 3,
    text = 'Normalize',
    relief = tk.GROOVE
)
bttn_normspec.pack()

bttn_spec = tk.Button(
    master = frame2,
    command = spectralizer,
    fg = 'black',
    bg = 'lightgrey',
    width = 10,
    height = 3,
    text = 'Draw Spectra',
    relief = tk.GROOVE
)
bttn_spec.pack()

bttn_wav = tk.Button(
    master = frame2,
    command = WavShow,
    fg = 'black',
    bg = 'lightgrey',
    width = 10,
    height = 3,
    text = 'Wavelength',
    relief = tk.GROOVE
)
bttn_wav.pack()

#having a reset button doesn't seem worth it on its own as you can just recalculate the spectra
##############################################
#frame for spectra
frame3 = tk.Frame(
    master = window,
    relief = tk.RAISED,
    borderwidth = 1
    )
frame3.grid(row=1, column=1)

figSpec = Figure(dpi = 100)
figSpec.add_subplot(111).plot(cmap = 'gray', norm ='normalize', interpolation='none')

canvasSpec = FigureCanvasTkAgg(figSpec, master = frame3)
canvasSpec.draw()
#testing if toolbar makes sense here, think it does
toolbar = NavigationToolbar2Tk(canvasSpec, frame3,)
toolbar.update()
canvasSpec.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand = 1)


def _quit(event):
    window.quit()
    window.destroy()

window.bind("<Escape>", _quit)



tk.mainloop()