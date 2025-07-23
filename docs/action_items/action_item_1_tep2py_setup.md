# Action Item 1: TEP Simulator Setup and Basic Usage

## Overview
This guide provides step-by-step instructions for setting up and running the TEP simulator using the `tep2py` Python wrapper on macOS.

## Prerequisites
- Python 3.6+
- pip
- gfortran (Fortran compiler)

## Steps
1. **Install Dependencies**
   ```bash
   pip install numpy pandas
   brew install gcc
   ```

2. **Compile the Fortran Code**
   ```bash
   cd /path/to/tep2py-master
   python -m numpy.f2py -c temain_mod-smart.pyf src/tep/temain_mod.f src/tep/teprob.f
   ```

3. **Run a Basic Simulation**
   ```python
   import numpy as np
   from tep2py import tep2py
   import pandas as pd

   # Initialize simulation
   n_points = 100
   idata = np.zeros((n_points, 20))
   tep = tep2py(idata)
   tep.simulate()
   print(tep.process_data.head())
   ```

4. **Triggering Faults**
   ```python
   # To trigger Fault 3 at step 50
   fault_start = 50
   fault_id = 3
   idata[fault_start:, fault_id-1] = 1
   ```

## Expected Output
- Successful compilation creates a `.so` file
- Simulation runs without errors
- Process data is printed to the console

## Troubleshooting
- **ImportError**: Ensure you're in the correct directory
- **Compilation Errors**: Verify gfortran installation
- **Version Mismatch**: Compile on target system

## Next Steps
- Proceed to Action Item 2 for fault analysis
- Experiment with different fault scenarios
- Save simulation results for further analysis
