<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20Logo%20V1%20no%20shade.png?token=GHSAT0AAAAAAC4D3YAIO64PHDLYUMRZHEYCZ4D6OFA" alt="DZHome Logo">
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
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/Data%20Formatting%20Example.png?token=GHSAT0AAAAAAC4D3YAIO4JOSZG3V7AMHXCAZ4D55AA" alt="Formatting Example">
</div>

DZHome requires the input data to follow a specific format. Input files must be Excel files (.xlsx) and follow the column header guide in the example dataset seen above. The following columns are required for data input:
- Sample ID 
- Best age 
- Error (1sig) 
- Long Axis (um)

Every analysis requires a sample ID, the Best Age, and the 1sigma error of that analysis. To use the HydroFrac module, long-axis measurements in um are also required but not needed for other modules.

## Getting Started
To begin, download the current version of DZHome. Once downloaded, relocate DZHome to the file directory where your data, or the test data, is stored. From here, DZHome can be opened in Jupyter Lab or Jupyter Notebook. Once open, simply run the code to get started!

## Data Input
<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20Data%20Input%20.png?token=GHSAT0AAAAAAC4D3YAJ5U45BGYKLU2J6CGKZ4D55NA" alt="DZHome Data Input">
</div>

The image above shows the initial data loading screen for DZHome. If your file is located in the same directory as DZHome and is an Excel Workbook file (.xlsx), the file can easily be located using the drop down menu. Once you have selected the file you want, press 'Load Data' to begin.

## Home Window
<div align="center">
  <img src="https://raw.githubusercontent.com/jackfekete01/DZHome/refs/heads/Assets/DZHome%20Home%20Screen.png?token=GHSAT0AAAAAAC4D3YAIJWCFAD6NHED4Z7YEZ4D55VA" alt="DZHome Data Input">
</div>

