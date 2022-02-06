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

#Initialize Consumer on topic input-stream
consumer_input = broker.initialize_consumer('input-stream')
producer_output = broker.initialize_producer()

def input_consumer_callback(message):
    #Apply JSON deserializer specificially for google pub sub
    if broker_choice=='Google_Pub_Sub':
        message.ack()
        message = json.loads(message.data.decode('utf-8'))

    #Apply Numpy deserializer
    batch = deserialization(message)
    prediction = get_model_prediction(batch, 'model.h5') #Assuming that model is saved as model.h5 in the same folder as the code file
    prediction = [int(x) for x in list(np.array(prediction))]
    print('Data consumed from input-stream:{}'.format(prediction))

    #Send prediciton list back to message broker
    broker.produce(producer_output, 'output-stream', prediction)
    return

broker.consume_and_close(consumer_input, input_consumer_callback)
