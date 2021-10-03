Other comments:
on manjaro tkinter:
xrdb -load /dev/null
xrdb -query
->should work

TODO
-save covariance matrix for calibration
-save metadata or similar
-cleanup comments for version 0.3.2 and remove commented code
-consider including a mechanism to export/import calibration settings



CHANGELOG:

0.3.1
polyfit now centers the data and also outputs the offset value
0.3.0
linear fitting has been fixed (here or in 0.2.3)
prints the covariance matrix if more than 3 data points are used for calibration
0.2.3 wip
added an option to input a name for the calibration as a way of telling to which series the calibration belongs
0.2.2
can use any pixel position for calibration, not just peaks found in spectra
0.2.0
show the used file name (both input and spectra)
swapped jpeg to be the first import option
Section in calibrator for tkinter of calibration has been rebuilt in a readable way
0.1.1 
fixed spectra saving mechanism for when no wavelength calibrated before saving
0.1 
Basic running version
Cut Picture save not verified yet