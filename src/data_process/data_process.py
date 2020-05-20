import sys
from data_processor import DataProcessor

if __name__ == "__main__":
    try:
        path_conf_source = sys.argv[1]
        x_data_processor = DataProcessor(path_conf_source)
    except Exception as err:
        print('########################################')
        print(' Error while launching data processor')
        print(repr(err))
        print('########################################')
