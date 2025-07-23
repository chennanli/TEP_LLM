#
# General instructions for completing README: 
# For sections that are non-applicable, mark as N/A (do not delete any sections). 
# Please leave all commented sections in README (do not delete any text). 
#

-------------------
GENERAL INFORMATION
-------------------

1. Title of Dataset: Dataset of Manipulations on the Tennessee Eastman Process

#
# Authors: Include contact information for at least the 
# first author and corresponding author (if not the same), 
# specifically email address, phone number (optional, but preferred), and institution. 
# Contact information for all authors is preferred.
#

2. Author Information
<create a new entry for each additional author>

First Author Contact Information
    Name: Clement Fung
    Institution: CyLab Security and Privacy Institute, Carnegie Mellon University
    Address: 4720 Forbes Ave, Pittsburgh, PA, 15213
    Email: clementf@andrew.cmu.edu

Corresponding Authors Contact Information
    Name: Lujo Bauer
    Institution: CyLab Security and Privacy Institute, Carnegie Mellon University
    Address: 4720 Forbes Ave, Pittsburgh, PA, 15213
    Email: lbauer@cmu.edu

---------------------
DATA & FILE OVERVIEW
---------------------

#
# Directory of Files in Dataset: List and define the different 
# files included in the dataset. This serves as its table of 
# contents. 
#

Directory of Files: /matlab-release/csv
  A. Filename: TEP_test_xxxx_yyy_zz.csv
      Short description: A stored trace of a manipulated TEP execution: Component zz is manipulated with a pattern of xxxx and magnitude of yyy.

Directory of Files: /matlab-release/
  A. Filename: process_matlab_TEP.py
      Data processing file used to format the CSVs in this dataset. Included for reference.
  
  B. Filename: README.md
      Additional README file.

Additional Notes on File Relationships, Context, or Content 
(for example, if a user wants to reuse and/or cite your data, 
what information would you want them to know?):              

Data was generated with a publicly available simulator, located at: 
https://github.com/pwwl/tep-attack-simulator

#
# File Naming Convention: Define your File Naming Convention 
# (FNC), the framework used for naming your files systematically 
# to describe what they contain, which could be combined with the
# Directory of Files. 
#

File Naming Convention: 

Each manipulation is named with the following settings:
- Manipulation type: one of ['cons', 'csum', 'line']
- Manipulation magnitude: one of ['p2s', 'm2s', 'p3s', 'p5s']
- Manipulation location: sensors ['s1'] or actuators ['a1'], where the number corresponds to the feature number in the simulator

#
# Data Description: A data description, dictionary, or codebook
# defines the variables and abbreviations used in a dataset. This
# information can be included in the README file, in a separate 
# file, or as part of the data file. If it is in a separate file
# or in the data file, explain where this information is located
# and ensure that it is accessible without specialized software.
# (We recommend using plain text files or tabular plain text CSV
# files exported from spreadsheet software.) 
#

-----------------------------------------
DATA DESCRIPTION FOR: [FILENAME]
-----------------------------------------
<create sections for each dataset included>

1. Number of variables:

  Values for 53 components (41 sensors and 12 actuators) are included.
  The last (54th) column in each file contains the attack label: 1 if the manipulation is occurring, and 0 if not.

2. Number of cases/rows: 

  Each file contains 96001 timesteps. 

3. Missing data codes:
        Code/symbol        Definition
        Code/symbol        Definition

  N/A

4. Variable List

#
# Example. Name: Gender 
#     Description: Gender of respondent
#         1 = Male
#         2 = Female
#         3 = Transgender
#	      4 = Nonbinary
#		  5 = Other gender not listed 
#		  6 = Prefer not to answer
#

  Each variable is a component in the TEP process: 41 sensors and 12 actuators.
  For more details, see the MATLAB simulator: https://github.com/pwwl/tep-attack-simulator

    A. Name: <variable name>
       Description: <description of the variable>
                    Value labels if appropriate


    B. Name: <variable name>
       Description: <description of the variable>
                    Value labels if appropriate

--------------------------
METHODOLOGICAL INFORMATION
--------------------------

#
# Software: If specialized software(s) generated your data or
# are necessary to interpret it, please provide for each (if
# applicable): software name, version, system requirements,
# and developer. 
#If you developed the software, please provide (if applicable): 
#A copy of the software’s binary executable compatible with the system requirements described above. 
#A source snapshot or distribution if the source code is not stored in a publicly available online repository.
#All software source components, including pointers to source(s) for third-party components (if any)

1. Software-specific information:
<create a new entry for each qualifying software program>

Name: TEP Attack Simulator
Version: N/A
System Requirements: MATLAB
Open Source? (Y/N): Y

(if available and applicable)
Executable URL: N/A

Source Repository URL: 
  Simulator: https://github.com/pwwl/tep-attack-simulator 

Developer: N/A
Product URL: N/A
Software source components: N/A

Additional Notes(such as, will this software not run on 
certain operating systems?):

Simulator requires MATLAB.

#
# Equipment: If specialized equipment generated your data,
# please provide for each (if applicable): equipment name,
# manufacturer, model, and calibration information. Be sure
# to include specialized file format information in the data
# dictionary.
#

2. Equipment-specific information:
<create a new entry for each qualifying piece of equipment>

N/A

Manufacturer:
Model:

(if applicable)
Embedded Software / Firmware Name:
Embedded Software / Firmware Version:
Additional Notes:

#
# Dates of Data Collection: List the dates and/or times of
# data collection.
#

3. Date of data collection (single date, range, approximate date) <suggested format YYYYMMDD>:

  Manipulations were generated approximately on 2022/04/01. 
