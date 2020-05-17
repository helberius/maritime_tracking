import json
import sys
import pika
import requests
import os


class PollingProxy:
    rabbit_connection = None

    def __init__(self, conf_json):
        filename  = os.path.basename(conf_json)
        try:
            with open(conf_json) as json_file:
                data = json.load(json_file)
                print(data)
                for e in data:
                    setattr(self, e, data[e])
                # setattr(self, "element_to_poll", data['element_to_poll'])
                # setattr(self, "rabbitmq_host", data['rabbitmq_host'])
                # setattr(self, "rabbitmq_port", data['rabbitmq_port'])
                # setattr(self, "rabbit_user", data['rabbit_user'])
                # setattr(self, "rabbit_pwd", data['rabbit_pwd'])
                # setattr(self, "rabbit_vhost", data['rabbit_vhost'])
                # setattr(self, "rabbit_exchange", data['rabbit_exchange'])
                # setattr(self, "rabbit_queue", data['rabbit_queue'])

        except Exception as err:
            print('Error while initializing the PollingProxy. I am exiting')
            print(repr(err))
            sys.exit(0)
        self.open_rabbit_connection()
        ls_info = self.get_data()
        self.push_msgs(ls_info)


    def get_data(self):
        try:
            response = requests.get(self.polling_source)
            json_response = response.json()
            element_to_poll = json_response[self.element_to_poll]
            return element_to_poll
        except Exception as err:
            print('##########################################')
            print('Error while requesting the data from the polling source')
            print(repr(err))
            print('##########################################')
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



    def push_msgs(self, ls_info):

        try:

            channel = self.rabbit_connection.channel()
            channel.queue_declare(queue=self.rabbit_queue, durable=True, )
            channel.queue_bind(exchange=self.rabbit_exchange, queue=self.rabbit_queue, routing_key=self.rabbit_queue)

            for e in ls_info:
                e['data_source']=self.data_source
                channel.basic_publish(exchange=self.rabbit_exchange,
                                      routing_key=self.rabbit_queue,
                                      body=json.dumps(e),
                                      properties=pika.BasicProperties(delivery_mode=2)
                                      )
            self.rabbit_connection.close()

        except Exception as err:
            print('##########################################')
            print('Error while submitting msgs')
            print(repr(err))
            print('##########################################')
            sys.exit(0)

