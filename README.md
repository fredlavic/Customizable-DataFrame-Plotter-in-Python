# Data Analysis and Graphic Output in Python (DAGO py)

A python code to generate detailed and customizable graphs based on the data in a [Pandas DataFrame](https://pandas.pydata.org/docs/index.html).

This code is mainly oriented to analyze GAMS Data eXchange (GDX) files, but any labeled data works as long as it can be transcribed into a DataFrame.

If you do not intend to use GDX files, you can skip the sections **Installation of GAMS API** and **Usage with GDX files**.

## Installation of GAMS API

The GAMS API is a Python package that facilitates interaction with the GAMS system and data exchange between GAMS and Python. Here are the key steps to get started:

1. **Verify Conda Installation**:
   - Ensure that Conda is accessible from the terminal by checking its version:
     ```
     $ conda --version
     conda 22.9.0
     ```
2. **Create a New Conda Environment**:
   - Create an isolated Python environment named "gams":
     ```
     $ conda create --name gams python=3.10
     ```
   - Activate the environment:
     ```
     $ conda activate gams
     ```
3. **Install the GAMS API**:
   
     For this code, we will use the *transfer* module of the GAMS API.
   
   - Use pip to install the GAMS Python API:
     ```
     (gams)$  pip install gamsapi[transfer]==xx.y.z
     ```
     `xx.y.z` represents the installed GAMS version number (e.g., 46.4.1)
     
Since a new environment has been created, some other usefull packages might need to be installed. 

If you encounter problems with this installation, the complete documentation guide is available in the [official GAMS API documentation](https://www.gams.com/latest/docs/API_PY_GETTING_STARTED.html).

## Usage with GDX files

