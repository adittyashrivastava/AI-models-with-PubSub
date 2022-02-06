import sys, json
from brokers import Broker
from numpy_converters import deserialization
from model_functions import get_model_prediction
import numpy as np


#Read choice of broker from the passed system arguement
broker_choice = sys.argv[1]

#Initiate broker
if broker_choice == 'Kafka':
    broker = Broker(broker_choice)
elif broker_choice == 'Google_Pub_Sub':
    broker = Broker(broker_choice, (sys.argv[2],  #Add JSON file name with credentials
                                    sys.argv[3])) #Add Project ID here

#Initialize Consumer on topic output-stream
consumer_output = broker.initialize_consumer('output-stream')

def output_consumer_callback(message):
    #Apply JSON deserializer specificially for google pub sub
    if broker_choice=='Google_Pub_Sub':
        message.ack()
        message = json.loads(message.data.decode('utf-8'))

    print('Following are the predictions from the input - {}'.format(message))
    return

broker.consume_and_close(consumer_output, output_consumer_callback)
