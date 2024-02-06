<div align="center">
  <img src="DZHome%20Logo%20V1%20no%20shade.png" alt="DZHome Logo">
</div>

# DZHome

DZHome is a Python GUI script that allows users to interact with detrital zircon U-Pb data sets by plotting data, creating maximum depositional age (MDA) approximations, comparing similarity/ dissimilarity metrics, and exploring the effects of hydrodynamic fractionation on DZ age populations. DZHome allows users to harness the analytical power of Python through an easy-to-use GUI. DZHome can be implemented via a Jupyter Notebook or Py file. 

## Installation
In order to use DZHome, users will need to download the required files from the DZHome branch. 

## Requirements
DZHome requires the following dependencies in order to function:
- tkinter
- matplotlib
- detritalpy
- numpy
- pandas
- os
- seaborn
- sklearn
- math
- scipy
- random
- time

## Data Formatting
<div align="center">
  <img src="Data%20Formatting%20Example.png" alt="Formatting Example">
</div>
DZHome requires the input data to follow a specific format. Input files must be Excel files (.xlsx) and follow the column header guide in the example dataset seen above. The following columns are required for data input:
- Sample ID
- Best age
- Error (1sig)
- Long Axis (um)

 Every analysis requires a sample ID, the Best Age, and the 1sigma error of that analysis. To use the HydroFrac module, Long Axis measurements in um are also required but not needed for other modules.
