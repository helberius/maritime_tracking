from polling_proxy.PollingProxy import PollingProxy

if __name__ == "__main__":
    # polling_proxy_digitraffic = PollingProxy("./configuration/digitraffic.json")
    # print(str(polling_proxy_digitraffic.__dict__))

    polling_proxy_quakes_usgs = PollingProxy("./configuration/usgs_quakes_all_hour.json")

    #polling_proxy_digitraffic = PollingProxy("./configuration/digitraffic.json")
