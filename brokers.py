#This file contains a class for every message broker to be configured
#with functions defined to be used to setup the data pipelines for the application required

import os
import numpy as np
from json import dumps, loads
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from numpy_converters import serialization, deserialization


#----------SETTING UP KAFKA------------#

class Broker:
    def __init__(self, broker, params=None):
        self.broker = broker

        if broker=='Kafka':
            self.__uri = os.environ.get('KAFKA_URI', '127.0.0.1:9092')
        elif broker=='Google_Pub_Sub':
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"], self.pub_sub_project = params
        else:
            raise Exception('''Broker can be one amongst the following values:
            1. Kafka
            2. Google_Pub_Sub''')

    #Error Callback function for signifying any errors while data transmission to Kafka
    def __kafka_err_callback(self, exc):
        raise Exception('Error while sendig data to kafka: {}'.format(str(exc)))

    #Initialize Producer for further usage
    def initialize_producer(self):
        if self.broker=='Kafka':
            #Initializing the Kafka Producer Instance
            producer = KafkaProducer(bootstrap_servers=[self.__uri],
                                     value_serializer=lambda x: dumps(x).encode('utf-8')
                                     )

            print('Producer is ready')
            return producer

        elif self.broker=='Google_Pub_Sub':
            #Initializing Google Pub Sub Producer instance
            publisher = pubsub_v1.PublisherClient()
            #topic_path = publisher.topic_path(self.pub_sub_project, topic)

            print('Publisher and topic path initialized')
            return publisher

    #Produce function to push message to topic from a producer instance
    def produce(self, producer, topic_name=None, X=None):
        if not X:
            raise Exception('Parse arguement for data to be produced')
        if not topic_name:
            raise Exception('Give a topic name to send data to')

        if self.broker=='Kafka':
            #Sending data to topic
            producer.send(topic_name,
                        value= X).add_errback(self.__kafka_err_callback)

            print("Wrote message into topic: {}\n{}".format(topic_name, X))

        elif self.broker=='Google_Pub_Sub':
            #Sending data to topic
            publisher = producer
            topic_path = publisher.topic_path(self.pub_sub_project, topic_name)
            data = dumps(X).encode("utf-8")
            future = publisher.publish(topic_path, data=data)
            print("Pushed message to topic - {}".format(X))

    #Initialize Consumer for further usage
    def initialize_consumer(self, topic_name:str):
        if self.broker=='Kafka':
            #Initializing the Kafka Consumer Instance
            consumer = KafkaConsumer(topic_name,
                                     bootstrap_servers=[self.__uri],
                                     auto_offset_reset='earliest',
                                     enable_auto_commit=True,
                                     group_id='my-group',
                                     value_deserializer=lambda x: loads(x.decode('utf-8')),
                                     consumer_timeout_ms=90000)

            print('Consumer is ready')
            return consumer

        elif self.broker=='Google_Pub_Sub':

            subscriber = pubsub_v1.SubscriberClient()
            subscription_path = subscriber.subscription_path(self.pub_sub_project, topic_name+'-sub')
            print(f"Listening for messages on {subscription_path}..\n")
            return (subscriber, subscription_path)

    #Consume function to listen to messages incoming in topic from a consumer instance
    def consume_and_close(self, consumer, callback):
        if self.broker=='Kafka':
            #Listen to incoming messages in topic
            for message in consumer:
                #key = message.key.decode('utf-8')
                message = message.value
                callback(message)

            #Close consumer if it remains inactive for more than 20 seconds
            consumer.close()

        elif self.broker=='Google_Pub_Sub':
            #Listen to incoming messages in topic
            subscriber, subscription_path = consumer
            streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
            # Wrap subscriber in a 'with' block to automatically call close() when done.
            with subscriber:
                try:
                    # When `timeout` is not set, result() will block indefinitely,
                    # unless an exception is encountered first.
                    consumption = streaming_pull_future.result(timeout=90)
                except TimeoutError:
                    streaming_pull_future.cancel()

    def close_producer(self, producer):
        if self.broker=='Kafka':
            #Close producer
            producer.flush()
            producer.close()
        elif self.broker=='Google_Pub_Sub':
            #Did not find a formal publisher client closing
            #python script. Can be added if found.
            return
