    # -*- coding: utf-8 -*-
"""
Created on Mon Nov 02 13:31:06 2015

@author: b.ellinger

This script converst a Python script to a *.exe using cx_freeze 4.3.4

To do so, follow these steps (in Power Shell):
I.  run: "python setup.py build"
II. For making plot-function working correctly several numpy *.dll files need to be imported to the *.exe folder.
    a. run: "cp %homepathPYTHON%\Lib\site-packages\numpy\core\mkl*.dll %homepath%\desired_EXE"
        e.g.:
        cp C:\WinPython-64bit-3.4.3.7\python-3.4.3.amd64\Lib\site-packages\numpy\core\mkl*.dll C:\_DATA\Kunden\OSP_Rheinland-Pfalz.Ullrich\application\v1.01\build\\exe.win-amd64-3.4
    b. run: "cp %homepathPYTHON%\Lib\site-packages\numpy\core\libiomp5md.dll %homepath%\desired_EXE"

    not sure how to do it with a MSI-installer
!!!Before doing so, be sure your script runs correctly!!!
"""

#import sys
#import cx_Freeze
#import matplotlib
#
#base = None
#if sys.platform == 'win32':
#    base="Win32GUI"
#
#executables = [cx_Freeze.Executable("MyMo_compa_Kist.py", base = base, icon="images\logo_osp.ico")]
#
#cx_Freeze.setup(
#    name = "OSP_BadKreuznach",
#    options = {"build_exe": {"packages": ["tkinter", "matplotlib"], "include_files":["images/logo_velamed.png"]}},
#    version = "0.5",
#    description = "OSP Bad Kreuznach Calculator",
#    executables = executables)

#
#import cx_Freeze
#import matplotlib
#import sys
#import numpy
#import tkinter
#import scipy
#
#base = None
#
#if sys.platform == "win32":
#    base = "Win32GUI"
#
#executables = [cx_Freeze.Executable('MyMo_compa_Kist.py', base=base, icon='images\logo_osp.ico')]
#
#
#build_exe_options = {"includes":   ["matplotlib.backends.backend_tkagg","matplotlib.pyplot",
#                             "tkinter.filedialog","numpy","scipy"],
#                     "include_files":[(matplotlib.get_data_path(), "mpl-data")],
#                     "excludes":[],
#                    }
#
#cx_Freeze.setup(
#    name = "MyoMotion_Kistler",
#    options = {"build_exe": build_exe_options},
#    version = "1.0",
#    description = 'OSP Bad Kreuznach Calculator_v1.0',
#    executables = executables)



#
import cx_Freeze
import sys
import matplotlib
import numpy
import tkinter
#import scipy

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [cx_Freeze.Executable('main.py', base=base, icon='images\logo_osp.ico')]

packages = ['tkinter','matplotlib','scipy']

include_files = ['logo_velamed.png', 'images\logo_osp.ico',(matplotlib.get_data_path(), "mpl-data")]

cx_Freeze.setup(
    name = 'MR3_Jump-analysis_v1.01',
    options = {'build_exe': {'packages':packages,
        'include_files':include_files}},
    version = '1.01',
    description = 'MR3_Jump-analysis_v1.01',
    executables = executables
    )
