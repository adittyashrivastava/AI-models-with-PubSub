'''
import numpy as np
from time import sleep
from json import dumps
from kafka import KafkaProducer

from numpy_converters import serialization

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))


for e in range(1000):
    data = serialization(np.random.randint(0, 256, (10,10,1)))
    producer.send('test_input', value=data)
    sleep(10)

from brokers import KafkaBroker
from time import sleep
import numpy as np
broker = KafkaBroker()
for e in range(5):
    k = np.random.randint(0, 256, (5,10,10))
    broker.produce('test_input', k[e, :, :], [e])
    sleep(10)


from brokers import GooglePubSubBroker
from time import sleep
import numpy as np
broker = GooglePubSubBroker("test_input", "clear-adapter-340306", "test_input-sub", "gcp-pubsub-broker-key.json")
k = np.random.randint(0, 256, (15,10,10))
for e in range(15):
    broker.produce('test_input', k[e, :, :])
    sleep(7)

'''

import sys, json, time
from brokers import Broker
from numpy_converters import serialization
import tensorflow as tf
import numpy as np

#Get test data from Fashion MNIST
fashion_mnist = tf.keras.datasets.fashion_mnist
_,(x_test, _) = fashion_mnist.load_data()
x_test = tf.expand_dims(x_test, axis=-1)

#Read choice of broker from the passed system arguement
broker_choice = sys.argv[1]

#Initiate broker
if broker_choice == 'Kafka':
    broker = Broker(broker_choice)
elif broker_choice == 'Google_Pub_Sub':
    broker = Broker(broker_choice, (sys.argv[2],  #Add JSON file name with credentials
                                    sys.argv[3])) #Add Project ID here

#Initialize Producer
producer_input = broker.initialize_producer()

#Sending a batch of 40 images from test data at a time
#till all 10000 images are sent by the producer

for i in range(int(10000/40)):
    #Get the batch of 40 images and serialize them
    batch = x_test[i*40:(i+1)*40, :, :, :]
    batch = serialization(np.array(batch))

    #Send it via producer to the topic input-stream
    broker.produce(producer_input, 'input-stream', batch)
    time.sleep(5)
