# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import time

if __name__ == "__main__":
    print(str(sys.argv))
    try:
        bool_autocloning = bool(os.environ['AUTOCLONING'])
        if bool_autocloning:
            ls_parameters=['git','pull','https://github.com/helberius/maritime_tracking.git']
            subprocess.call(ls_parameters, shell=False, cwd="/maritime_tracking")
    except Exception as err:
        print(repr(err))