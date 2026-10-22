Week 6: Regional climate with a 1D energy balance model

1. Download week06_labs.zip from the course website and unzip it.
2. Keep the notebook, this file, the requirements file, and the data folder together.
3. Open latitude_ebm.ipynb in Jupyter, for example on the LEAP hub.
4. Run cells in order and fill in the Answer spaces under Lab questions.

All model code is supplied. There is one short question in each of eight sections.
Section 5 (diffusion alone) is optional. Explore how absorbed sunlight, outgoing
infrared radiation, and horizontal heat transport determine the temperature profile.

Python packages: NumPy, SciPy, Matplotlib, xarray, netCDF4, and Jupyter/IPython.
week06_requirements.txt records the versions used to check the notebook.

The package includes NOAA's public 1981–2010 NCEP–NCAR surface skin-temperature
climatology in data/ncep/skt.sfc.mon.1981-2010.ltm.nc. It can therefore run offline.
If this file is missing, the notebook downloads it from NOAA and caches it in the
same location. The CERES radiation-budget and NCEP-based reference figures are
embedded in the notebook.

Save your work in your course GitHub repository. Follow the lab and submission
instructions on the course website and Courseworks.

Course site: https://dhruvbalwada.github.io/intro-climate-modeling-fall2026/
