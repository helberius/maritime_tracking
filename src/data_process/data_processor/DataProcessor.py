import json
import sys
import pika
import os
from elasticsearch import Elasticsearch
import datetime
import pandas as pd

class DataProcessor:
    rabbit_connection = None
    channel = None
    elastic_search = None


    def __init__(self, conf_json):
        try:
            with open(conf_json) as json_file:
                data = json.load(json_file)
                print(data)
                for e in data:
                    setattr(self, e, data[e])
            self.rabbitmq_host = os.environ['RABBIT_HOST']
            self.open_rabbit_connection()
            self.open_elastic_connection()
            self.get_messages()

        except Exception as err:
            print('Error while initializing the DataProcessor. I am exiting')
            print(repr(err))
            sys.exit(0)


    def open_rabbit_connection(self):
        try:
            credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_pwd)

            connection_parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                heartbeat=0,
                credentials=credentials,
                virtual_host=self.rabbit_vhost
            )
            self.rabbit_connection = pika.BlockingConnection(connection_parameters)


        except Exception as err:
            print('##########################################')
            print('Error while creating the connection')
            print(repr(err))
            print('##########################################')
            sys.exit(0)

    def on_message(self,channel, method_frame, header_frame, body):

        json_msg = json.loads(body)

        try:
            id_position =str(json_msg['properties']['mmsi']) + '_' + str(json_msg['properties']['timestampExternal'])
            res = self.elastic_search.index(index='digitraffic_pos', doc_type = 'doc', id= id_position, body = json_msg)
            updated_info_vessel = self.get_info_vessel( json_msg['properties']['mmsi'], self.elastic_search)

            if updated_info_vessel is not None:
                res2 = self.elastic_search.index(index='digitraffic_vessels', doc_type = 'doc', id= json_msg['properties']['mmsi'], body = updated_info_vessel)



            self.channel.basic_ack(delivery_tag = method_frame.delivery_tag)


        except Exception as err:
            print('##########################################')
            print('Error while inserting one record in elasticsearch')
            print(repr(err))
            print('##########################################')
            sys.exit(0)

    def get_messages(self):
        try:
            self.open_rabbit_connection()
            self.channel = self.rabbit_connection.channel()
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(self.rabbit_queue, self.on_message, auto_ack=False)
            self.channel.start_consuming()


        except Exception as err:
            print('##########################################')
            print('Error while submitting msgs')
            print(repr(err))
            print('##########################################')
            sys.exit(0)


    def open_elastic_connection(self):
        try:
            self.elastic_search = Elasticsearch([{'host':'elasticsearch','port':9200}])
        except Exception as err:
            print('##################################')
            print('Error while opening connection to elasticsearch')
            print('##################################')
            sys.exit(0)

    def get_info_vessel(self,x_mmsi, elastic_search_connection):
        try:
            print('* calculating: ', x_mmsi)
            # elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
            # elastic_search_connection.indices.refresh("digitraffic_vessels")

            search_params_points = {
                'size': 10000,
                "query":
                    {
                        "bool": {
                            "must": [
                                {"match": {"mmsi": x_mmsi}}
                            ]
                        }
                    }
            }

            res_points = elastic_search_connection.search(index="digitraffic_pos", doc_type="doc",
                                                          body=search_params_points)
            res_points_hits = res_points['hits']['hits']

            ls_pts = []
            for num2, doc2 in enumerate(res_points_hits):
                x_pt = {
                    'mmsi': x_mmsi,
                    'timestampExternal': doc2['_source']['properties']['timestampExternal'],
                    'lat': doc2['_source']['geometry']['coordinates'][1],
                    'lng': doc2['_source']['geometry']['coordinates'][0]
                }
                ls_pts.append(x_pt)

            df_pts = pd.DataFrame(data=ls_pts)
            # print(x_mmsi,df_pts.shape)
            if df_pts.shape[0] > 1:
                data_max = df_pts.max(axis=0)
                data_min = df_pts.min(axis=0)
                data_stddev = df_pts.std(axis=0)
                data_mean = df_pts.mean(axis=0)

                dict_max = {}
                for index, value in data_max.items():
                    dict_max[index] = value
                dict_min = {}
                for index, value in data_min.items():
                    dict_min[index] = value
                dict_stddev = {}
                for index, value in data_stddev.items():
                    dict_stddev[index] = value
                dict_mean = {}
                for index, value in data_mean.items():
                    dict_mean[index] = value

                # most recent information

                series_most_recent_info = df_pts[df_pts['timestampExternal'] == dict_max['timestampExternal']].iloc[0]
                print('--- most recent point ---')
                dict_most_recent_info = {}
                for index, value in series_most_recent_info.items():
                    dict_most_recent_info[index] = value
                dict_most_recent_info['date'] = datetime.datetime.fromtimestamp(
                    dict_most_recent_info['timestampExternal'] / 1000).strftime(
                    '%Y-%m-%d %H:%M:%S')

                dict_info_mmsi = {"mmsi": int(x_mmsi),
                                  "pt_count": df_pts.shape[0],
                                  "timestamp_min": dict_min['timestampExternal'],
                                  "timestamp_max": dict_max['timestampExternal'],
                                  "timestamp_mean": dict_mean['timestampExternal'],
                                  "timestamp_std": dict_stddev['timestampExternal'],
                                  "delta_time_hrs": (((dict_max['timestampExternal'] - dict_min[
                                      'timestampExternal']) / 1000) / 60) / 60,
                                  "date_o": datetime.datetime.fromtimestamp(
                                      dict_min['timestampExternal'] / 1000).strftime(
                                      '%Y-%m-%d %H:%M:%S'),
                                  "date_f": datetime.datetime.fromtimestamp(
                                      dict_max['timestampExternal'] / 1000).strftime(
                                      '%Y-%m-%d %H:%M:%S'),
                                  "date_mean": datetime.datetime.fromtimestamp(
                                      data_mean['timestampExternal'] / 1000).strftime(
                                      '%Y-%m-%d %H:%M:%S'),
                                  "lat_min": dict_min['lat'],
                                  "lat_max": dict_max['lat'],
                                  "lat_mean": dict_mean['lat'],
                                  "lat_std": dict_stddev['lat'],
                                  "lng_min": dict_min['lng'],
                                  "lng_max": dict_max['lng'],
                                  "lng_mean": dict_mean['lng'],
                                  "lng_std": dict_stddev['lng'],
                                  'most_recent_info': dict_most_recent_info
                                  }
                return dict_info_mmsi
            else:
                dict_info_mmsi = {"mmsi": int(x_mmsi),
                                  "pt_count": df_pts.shape[0]}
                return dict_info_mmsi

        except Exception as err:
            print('************ Exception while calculating vessel info ***************')
            print(repr(err))
            print('********************************************************************')