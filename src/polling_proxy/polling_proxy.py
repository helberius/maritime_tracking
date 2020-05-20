# -*- coding: utf-8 -*-
from polling_proxy.PollingProxy import PollingProxy
import sys
import time

if __name__ == "__main__":
    print(str(sys.argv))
    try:
        path_conf_source = sys.argv[1]
        polling_proxy = PollingProxy(path_conf_source)

    except Exception as err:
        print(repr(err))
