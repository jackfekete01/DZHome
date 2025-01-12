<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20Logo%20V1%20no%20shade.png" alt="DZHome Logo">
</div>

# DZHome

DZHome is a Python GUI script that allows users to interact with detrital zircon U-Pb data sets by plotting data, creating maximum depositional age (MDA) approximations, comparing similarity/ dissimilarity metrics, and exploring the effects of hydrodynamic fractionation on DZ age populations. DZHome allows users to harness the analytical power of Python through an easy-to-use GUI. DZHome can be implemented via a Jupyter Notebook file. 

## Installation
To use DZHome, users will need to download the required files from the DZHome branch. 

## Requirements
DZHome requires the following dependencies to function:
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
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/Data%20Formatting%20Example.png" alt="Formatting Example">
</div>

DZHome requires the input data to follow a specific format. Input files must be Excel files (.xlsx) and follow the column header guide in the example dataset seen above. The following columns are required for data input:
- Sample ID 
- Best age 
- Error (1sig) 
- Long Axis (um)

Every analysis requires a sample ID, the Best Age, and the 1sigma error. Long-axis measurements in um are also required for the HydroFrac module but are not needed for other modules.

## Getting Started
To begin, download the current version of DZHome. Once downloaded, relocate DZHome to the file directory where your data, or the test data, is stored. From here, DZHome can be opened in Jupyter Lab or Jupyter Notebook. Once open, run the code to get started!

## Data Input
<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20Data%20Input%20.png" alt="DZHome Data Input">
</div>

The image above shows the initial data loading screen for DZHome. If your file is an Excel Workbook file (.xlsx) located in the same directory as DZHome, you can easily locate it using the drop-down menu. Once you have selected the file you want, press 'Load Data' to begin.

## Home Window
<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20Home%20Screen.png" alt="DZHome Data Input">
</div>

Once you have selected your data, DZHome will bring you to the home window. Here, users can see the data they have input and select one of DZHome's four main functions. 
- Plot: a plotting function that allows users to visualize their detrital zircon data
- Stats: a function that allows for comparison and basic visualization of samples
- MDA: calculate maximum depositional age approximation from samples and visualize these approximations in ranked-date plots or pair date-KDE plots
- Hydrofrac: calculate the amount of hydrodynamic fractionation present in your dataset

## Plot
<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20-%20Plot%20Image.PNG" alt="DZHome Plot Page">
</div>

The Plot function allows users to visualize their data easily through various plotting combinations. Plotting multiple or individual samples can be done by following the steps listed on the plotting page, which are outlined below.

### 1) Select Samples
Clicking 'Select Samples' will open a new window with all samples from the dataset. Clicking a sample adds it to the list of samples to be plotted. Note that the order in which the samples are selected will be the order in which the samples are plotted. Samples can also be removed from the list by clicking them.

### 2) Select Plot Type
Three types of plots can be generated using the plot function:
- KDE
- PDP
- CDF

If plotting a KDE, the bandwidth can be specified in the box below. If not specified, a default value of 10 Myr will be used. 
