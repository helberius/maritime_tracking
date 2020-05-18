import json
import sys
import pika

class DataProcessor:
    rabbit_connection = None
    channel = None


    def __init__(self, conf_json, rabbitmq_host):
        try:
            with open(conf_json) as json_file:
                data = json.load(json_file)
                print(data)
                for e in data:
                    setattr(self, e, data[e])
            self.rabbitmq_host = rabbitmq_host
            self.open_rabbit_connection()
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
        print(body)
        json_msg = json.loads(body)
        self.channel.basic_ack(delivery_tag = method_frame.delivery_tag)

    def get_messages(self):
        try:
            self.open_rabbit_connection()
            self.channel = self.rabbit_connection.channel()

            self.channel.basic_consume(self.rabbit_queue, self.on_message)
            self.channel.start_consuming()


        except Exception as err:
            print('##########################################')
            print('Error while submitting msgs')
            print(repr(err))
            print('##########################################')
            sys.exit(0)