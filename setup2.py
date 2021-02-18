# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 22:26:32 2016

@author: b.ellinger
"""

import cx_Freeze
import matplotlib.pyplot
import matplotlib.backends.backend_tkagg
import sys
import numpy
import scipy
import tkinter

base = None

if sys.platform == "win32":
    base = "Win32GUI"

#packages = ["tkinter", "matplotlib.pyplot", 'matplotlib.backends.backend_tkagg']
executables = [cx_Freeze.Executable("MyMo_compa_Kist.py", base=base, icon="images\logo_osp.ico")]


build_exe_options = {"includes":["matplotlib.backends.backend_tkagg","matplotlib.pyplot",
                                 "tkinter.filedialog","numpy","scipy.integrate"],
                     "include_files":[(matplotlib.get_data_path(), "mpl-data")],
                     "excludes":[],
                     }

cx_Freeze.setup(
    name = "teste mal",
    options = {"build_exe": build_exe_options},
    version = "1.0",
    description = "OSP Bad Kreuznach Calculator_v1.0",
    executables = executables)
