from elasticsearch import Elasticsearch
import pandas as pd

import sys
import datetime
from geopy.distance import geodesic
from geopy import distance
import json


def open_elastic_connection():
    try:
        elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        return elastic_search
        print('connection is open')
    except Exception as err:
        print('##################################')
        print('Error while opening connection to elasticsearch')
        print('##################################')
        sys.exit(0)

def count_docs_in_index():
    try:
        elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search.indices.refresh("info")
        res = elastic_search.cat.count("info", params={"format": "json"})

        return res[0]['count']
    except Exception as err:
        print(repr(err))

def get_n_docs_in_index(n):
    try:
        elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search.indices.refresh("info")
        # res = elastic_search.cat.search("info", params={"format": "json"}, body={"query":{}}, size=10)
        res = elastic_search.search(index="info", doc_type="doc", body={
            'size': n,
            'query': {
                'match_all': {}
            }
        })
        res_hits = res['hits']['hits']
        for num, doc in enumerate(res_hits):
            print('\n', num, '--', doc)



    except Exception as err:
        print(repr(err))


def get_docs_for_mmsi(mmsi):
    try:
        elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search.indices.refresh("info")
        #
        search_params={
            "query":
                {
                    "bool": {
                        "must": [
                            {"match": {"mmsi": mmsi}}
                        ]
                    }
                }
        }

        res = elastic_search.search(index="info", doc_type="doc", body=search_params)
        res_hits = res['hits']['hits']
        for num, doc in enumerate(res_hits):
            print('\n', num, '--', doc)

    except Exception as err:
        print(repr(err))

def scan_all_db_3(total_count):
    try:
        i_step_size = 10000
        ls_partial_results = []


        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        query_params = {
            'size': i_step_size,
            'query': {
                'match_all': {}
            }
        }
        res_original = es.search(index='info', body=query_params, scroll='1m')
        res_hits = res_original['hits']['hits']
        scrollId = res_original['_scroll_id']
        ls_partial_results.append(process_hits(res_hits))

        i_current_position = i_step_size
        while (total_count>i_current_position):
            res_sec = es.scroll(scroll_id=scrollId, scroll='10m')
            scrollId = res_sec['_scroll_id']
            res_hits_sec = res_sec['hits']['hits']
            ls_partial_results.append(process_hits(res_hits_sec))
            i_current_position = i_current_position + i_step_size
            print(i_current_position)

        ls_mmsi, ls_timestamp_info, ls_timestampExternal = process_partial_results(ls_partial_results)
        print(len(ls_mmsi))
        print(len(ls_timestampExternal))

    except Exception as err:
        print(repr(err))

def process_partial_results(ls_results):
    ls_mmsi =[]
    ls_timestamp_info =[]
    ls_timestampExternal =[]

    for r in ls_results:
        ls_mmsi = ls_mmsi + list(set(r[0])-set(ls_mmsi))
        ls_timestamp_info = ls_timestamp_info + list(set(r[1]) - set(ls_timestamp_info))
        ls_timestampExternal = ls_timestampExternal + list(set(r[2]) - set(ls_timestampExternal))

    return ls_mmsi, ls_timestamp_info, ls_timestampExternal

def process_hits(res_hits):
    ls_mmsi =[]
    ls_timestamp_info =[]
    ls_timestampExternal =[]

    for num, doc in enumerate(res_hits):
        if doc['_source']['mmsi'] not in ls_mmsi:
            ls_mmsi.append(doc['_source']['mmsi'])
        timestamp_info = str(doc['_source']['properties']['mmsi']) + '_' + str(
            doc['_source']['properties']['timestamp'])
        if timestamp_info not in ls_timestamp_info:
            ls_timestamp_info.append(timestamp_info)
        if doc['_source']['properties']['timestampExternal'] not in ls_timestampExternal:
            ls_timestampExternal.append(doc['_source']['properties']['timestampExternal'])
    return [ls_mmsi, ls_timestamp_info, ls_timestampExternal]



def scan_all_db_2(total_count_docs):
    try:
        client = Elasticsearch([{'host': 'localhost', 'port': 9200}])

        ls_mmsi=[]
        ls_timestamp_info =[]
        ls_timestampExternal=[]

        ifrom = 0
        step_size= 10000
        while ifrom < total_count_docs:
            search_body = {
                "from":ifrom,
                "size": 10000,
                "query": {
                    "match_all": {}
                }
            }
            ifrom = ifrom + step_size

            # resp = client.search(
            #     index="info",
            #     body=search_body
            # )

            resp = client.search(
                index="info",
                body=search_body,
                scroll='3m',  # time value for search
            )
            res_hits = resp['hits']['hits']

            for num, doc in enumerate(res_hits):
                if doc['_source']['mmsi'] not in ls_mmsi:
                    ls_mmsi.append(doc['_source']['mmsi'])
                timestamp_info = str(doc['_source']['properties']['mmsi']) + '_' + str(doc['_source']['properties']['timestamp'])
                if timestamp_info not in ls_timestamp_info:
                    ls_timestamp_info.append(timestamp_info)

                if doc['_source']['properties']['timestampExternal'] not in ls_timestampExternal:
                    ls_timestampExternal.append( doc['_source']['properties']['timestampExternal'])

            print('******** partial results *********')
            print('********', ifrom)
            print(search_body)
            print('******** count unique mmsi', len(ls_mmsi))
            print('******** count unique timestamp_info', len(ls_timestamp_info))
            print('******** count unique timestampExternal', len(ls_timestampExternal))
            print('****************************************')

        print('##### final count  #####')
        print('##### count unique mmsi', len(ls_mmsi))
        print('##### count unique timestamp_info', len(ls_timestamp_info))
        print('##### count unique timestampExternal', len(ls_timestampExternal))

        #print(ls_mmsi)


    except Exception as err:
        print(repr(err))

def process_all_db():
    try:
        elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search.indices.refresh("info")
        res = elastic_search.search(index="info", doc_type="doc", body={
            'size': 100000,
            'query': {
                'match_all': {}
            }
        })
        res_hits = res['hits']['hits']
        ls_mmsi=[]
        for num, doc in enumerate(res_hits):
            if doc['_source']['mmsi'] not in ls_mmsi:
                ls_mmsi.append(doc['_source']['mmsi'])
        print(len(ls_mmsi))
        print(ls_mmsi)


    except Exception as err:
        print(repr(err))


def get_list_distinct_mmsi():

    try:
        elastic_search = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search.indices.refresh("info")


        query={
                "size":0,
                "aggs" : {
                    "uniq_mmsi" : {
                        "terms" : { "field" : "mmsi" }
                    }
                }
            }

        res = elastic_search.search(index="info", doc_type="doc", body=query)
        res_hits = res['hits']['hits']
        print(res)
        for num, doc in enumerate(res_hits):
            print('\n', num, '--', doc)
    except Exception as err:
        print(repr(err))


def get_info_vessel(x_mmsi, elastic_search_connection):
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

        res_points = elastic_search_connection.search(index="digitraffic_pos", doc_type="doc", body=search_params_points)
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

            series_most_recent_info=df_pts[df_pts['timestampExternal']==dict_max['timestampExternal']].iloc[0]
            print('--- most recent point ---')
            dict_most_recent_info={}
            for index, value in series_most_recent_info.items():
                dict_most_recent_info[index]=value
            dict_most_recent_info['date']= datetime.datetime.fromtimestamp(dict_most_recent_info['timestampExternal']/1000).strftime(
                                  '%Y-%m-%d %H:%M:%S')


            dict_info_mmsi = {"mmsi": x_mmsi,
                              "pt_count": df_pts.shape[0],
                              "timestamp_min": dict_min['timestampExternal'],
                              "timestamp_max": dict_max['timestampExternal'],
                              "timestamp_mean": dict_mean['timestampExternal'],
                              "timestamp_std": dict_stddev['timestampExternal'],
                              "delta_time_hrs": (((dict_max['timestampExternal'] - dict_min[
                                  'timestampExternal']) / 1000) / 60) / 60,
                              "date_o": datetime.datetime.fromtimestamp(dict_min['timestampExternal'] / 1000).strftime(
                                  '%Y-%m-%d %H:%M:%S'),
                              "date_f": datetime.datetime.fromtimestamp(dict_max['timestampExternal'] / 1000).strftime(
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
                              'most_recent_info':dict_most_recent_info
                              }
            return dict_info_mmsi
        else:
            return None

    except Exception as err:
        print('************ Exception while calculating vessel info ***************')
        print(repr(err))
        print('********************************************************************')

def points_per_mmsi():
    try:
        elastic_search_connection = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search_connection.indices.refresh("digitraffic_vessels")


        search_params={
            'size':10000,
            'query': {
                'match_all': {}
            }
        }
        res = elastic_search_connection.search(index="digitraffic_vessels", doc_type="doc", body=search_params)
        res_hits = res['hits']['hits']
        # ls_mmsi=[]
        # print(len(res_hits))
        ls_info_vessels = []

        for num, doc in enumerate(res_hits):

            dict_vessel_info = get_info_vessel(doc['_source']['mmsi'], elastic_search_connection)
            if dict_vessel_info is not None:
                print('      adding: ', dict_vessel_info['mmsi'])
                ls_info_vessels.append(dict_vessel_info)


        path_info_mmsi = '/mnt/disk2/experiments/maritime_tracking/src/tmp/info_mmsi.csv'
        df_info_mmsi=pd.DataFrame(data =  ls_info_vessels)

        df_info_mmsi.to_csv(path_info_mmsi)


    except Exception as err:
        print(repr(err))

def get_vessels_trayectory():
    try:
        min_number_of_pts = 850
        elastic_search_connection = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        elastic_search_connection.indices.refresh("digitraffic_vessels")

        search_params = {
            'size':10000,
            "query":{
                "range": {
                     "pt_count": {
                         "gte": min_number_of_pts
                     }
                }
            }
        }

        print(search_params)
        res = elastic_search_connection.search(index="digitraffic_vessels", doc_type="doc", body=search_params)

        res_hits = res['hits']['hits']
        ls_vessels=[]
        for num, doc in enumerate(res_hits):
            dict_vessel =doc['_source']
            ls_vessels.append(dict_vessel)

        print('total vessels in result: ', len(ls_vessels))
        # x_vessel ={'mmsi':636018113}
        # ls_vessels = []
        # ls_vessels.append(x_vessel)
        count_vessels = 0
        ls_geojson_segments=[]
        for vessel in ls_vessels:
            search_pts =  {
                "size":10000,
                "query":{
                    "bool": {
                        "must": [
                            {"match": {"mmsi": vessel['mmsi']}}
                        ]
                    }
                },
                "sort":[{"properties.timestampExternal":"asc"}]
            }
            res_pts = elastic_search_connection.search(index="digitraffic_pos", doc_type="doc", body=search_pts)
            res_pts_hits = res_pts['hits']['hits']
            ls_pts = []

            for num, pt in enumerate(res_pts_hits):
                dict_pt = pt['_source']
                ls_pts.append(dict_pt)

            pt_o= ls_pts[0]
            pt_o['xtra_info']={}
            threshold_temporal = 720 # 12 hours in minutes
            ls_segments_trayectory=[]
            id_trajectory = 0


            ls_segments_trayectories=[]

            ls_trayectories=[]
            ls_trayectory=[pt_o]
            for i in range(1,len(ls_pts)):
                pt_x = ls_pts[i]
                delta_time_min = ((pt_x['properties']['timestampExternal']- pt_o['properties']['timestampExternal'])/1000)/60
                # if the delta time is higher than the threshold, then the point belong to a different trayectory
                # too much time between points, i assume that because of the big interval, the points belong to two different trayectories
                if delta_time_min> threshold_temporal:
                    ls_trayectories.append(ls_trayectory)

                    ls_trayectory = []
                    ls_segments_trayectory =[]
                    ls_trayectory.append(pt_x)
                    id_trajectory = id_trajectory + 1
                else:
                    coords_o = (pt_o['geometry']['coordinates'][1], pt_o['geometry']['coordinates'][0])
                    coords_x = (pt_x['geometry']['coordinates'][1], pt_x['geometry']['coordinates'][0])
                    distance_since_prev_point = distance.distance(coords_o, coords_x).km
                    delta_time_hours = delta_time_min / 60

                    pt_x['xtra_info'] = {}

                    pt_x['xtra_info']['distance_since_prev_point'] = distance_since_prev_point
                    pt_x['xtra_info']['speed_since_prev_point'] = distance_since_prev_point/delta_time_hours
                    pt_x['xtra_info']['delta_time_minutes'] = delta_time_min


                    #print(coords_o)
                    #print(coords_x)
                    #print(pt_x)
                    x_segment = create_linestring(coords_o, coords_x, pt_x['xtra_info'], vessel['mmsi'], id_trajectory)

                    ls_geojson_segments.append(x_segment)

                    ls_trayectory.append(pt_x)

                pt_o = pt_x


            ls_trayectories.append(ls_trayectory)
            print(count_vessels, vessel['mmsi'], len(ls_pts), len(ls_trayectories))
            count_vessels=count_vessels+1

        trajectory_feature_collection = {'type': 'FeatureCollection', 'features': ls_geojson_segments}

        path_json_file = '/mnt/disk2/experiments/maritime_tracking/src/tmp/trajectories.json'
        with open(path_json_file, 'w') as f:
            json.dump(trajectory_feature_collection, f)


    except Exception as err:
        print('----------------------------------------------------')
        print('Exception while requesting vesels with suitable information')
        print(repr(err))
        print('----------------------------------------------------')

def create_linestring(pt_o,pt_f, xtra_info, mmsi, id_trajectory):
    ls_pt_o = [pt_o[1],pt_o[0]]
    ls_pt_f = [pt_f[1],pt_f[0]]

    line_segment={
        "type":"Feature",
        "geometry":  {
        'type': 'LineString',
        'coordinates':[ls_pt_o, ls_pt_f]
        },
        "properties":{
            'distance': xtra_info['distance_since_prev_point'],
            'speed': xtra_info['speed_since_prev_point'],
            'delta_time_minutes': xtra_info['delta_time_minutes'],
            'mmsi': mmsi,
            'id_trajectory':id_trajectory
        }
    }

    return line_segment

if __name__ == "__main__":
    try:
        get_vessels_trayectory()
#        points_per_mmsi()

#     #    get_docs_for_mmsi(273332470)
#
#         #get_list_distinct_mmsi()
#         total_count = count_docs_in_index()
#         #scan_all_db_2(int(total_count))
#
#         scan_all_db_3(int(total_count))
#
#     #        get_n_docs_in_index(10)
#
#         #get_list_distinct_mmsi()
#
# #         elastic_search =  open_elastic_connection()
# #         #query =  {"query":{"match":{}}}
# #         query = {"query":{"size": 10}}
# #         res =  elastic_search.search(index ="info", body={"query":query})
# #         res_hits = res['hits']['hits']
# #         for num, doc in enumerate(res_hits):
# #             print('\n', num, '--', doc)
# # #        res = elastic_search.index(index='info', doc_type='doc', body=json_msg)
    except Exception as err:
        print(repr(err))

