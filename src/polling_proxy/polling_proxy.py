# -*- coding: utf-8 -*-
from polling_proxy.PollingProxy import PollingProxy
import sys
import time

if __name__ == "__main__":
    print(str(sys.argv))
    try:
        path_conf_source = sys.argv[1]
        periodicity = sys.argv[2]
        rabbit_host = sys.argv[3]

        periodicity_seconds = float(periodicity) *60
        polling_proxy = PollingProxy(path_conf_source, rabbit_host)
        while True:
            polling_proxy.get_data()
            time.sleep(periodicity_seconds)
    except Exception as err:
        print(repr(err))

    #polling_proxy_quakes_usgs = PollingProxy("./configuration/usgs_quakes_all_hour.json")

    #polling_proxy_digitraffic = PollingProxy("./configuration/digitraffic.json")
