import os
import warnings

import numpy as np
import pandas as pd

os.environ["LOG_LEVEL"] = "DEBUG"

try:
    get_ipython().run_line_magic("load_ext", "autoreload")  # noqa
    get_ipython().run_line_magic("autoreload", "2")  # noqa
    get_ipython().run_line_magic("matplotlib", "inline")  # noqa

    print("Loaded extensions")
except Exception:
    pass

warnings.filterwarnings("ignore")
print("Disabled warnings")

pd.set_option("display.float_format", lambda x: "%.5f" % x)
np.set_printoptions(suppress=True)
print("Set up Pandas and Numpy")
