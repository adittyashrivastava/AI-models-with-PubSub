# Image Classifier Integrated with Apache Kafka and Google Pub/Sub

**INTRODUCTION :**
This project entails -  
1. Setting up a single node cluster of Apache Kafka, and Google Pub/Sub message brokers.
2. Creating topics and subscribers in the message brokers to complete initial setup for creating required data pipelines.
3. Creating a Broker class for performing operations seamlessly via code and also ensuring possibility of integrating a new broker in the future, if required.
4. Developing a CNN based image classifier trained on the Fashion MNIST Dataset.
5. Creation of data pipelines for producer input, consumer input, producer output and consumer output data streams.

**STEP 1 :**
First we will setup Zookeeper and Kafka on the localhost, and get them up and running. You can skip this step if you have them up and running already. Find the steps to install Zookeeper and Kafka [here](https://www.tutorialspoint.com/apache_kafka/apache_kafka_installation_steps.htm) and have them up and running.

**STEP 2 :**
Open the command line and enter the directory Kafka (wherever you have the application modules stored) and run the following commands to generate the Kafka topics "input-stream" and "output-stream" -
```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic input-stream --partitions 1 --replication-factor 1
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic output-stream --partitions 1 --replication-factor 1
```
This command assumes that Kafka is running on localhost and is listening at the port 9092. You can change the argument for bootstrap server to a suitable URI if the case is different for you.

**STEP 3 :**
Now we need to setup Google Pub/Sub, it's topics and subscribers.
A GCP Service Account and private key are needed to access the Pub/Sub service from a Python application.
The full list of your service accounts can be accessed [here](https://console.cloud.google.com/iam-admin/serviceaccounts) and a new service account can be added using this [link](https://console.cloud.google.com/iam-admin/serviceaccounts/create). Give your account a name and id —  both can be the same but the id must be unique.

Click create and add the Pub/Sub Publisher and Pub/Sub Subscriber roles to ensure that this account can both consume data from and publish data to your Pub/Sub topic(s).

From here you can click done.
Next, we need to generate a private key that our Python application will use when communicating with GCP. Find the service account you just created and select the Manage keys option.

Use the Add Key button to add a new JSON key.

Clicking Create should download the private key file to your default Downloads directory. If we open the file we should see a JSON dictionary. Add this JSON file to the project folder. It contains credentials for creating an authorised connection to Google PubSub.

**STEP 4 :**
Before we can push/pull data from Pub/Sub we need to create a topic. You can see all your active topics [here](https://console.cloud.google.com/cloudpubsub/topic/list). Create new topics, with the names 'input-stream' and 'output-stream', and LEAVE THE DEFAULT SUBSCRIPTION OPTION CHECKED. Your default subscriptions will have the name of your topic with a "-sub" suffix.

Please take note of your Project ID and the name of our JSON file downloaded in step 3. You can find the Project ID on the Pub/Sub [list page](https://console.cloud.google.com/cloudpubsub/topic/list). It would be the value between projects and topics - projects/{Project ID}/topics/...

**STEP 5 :**
We have completed the required setup and now we can go ahead with firing the code up!
Open up 3 new command line interfaces and navigate to the project directory in each of them. I will be referring to them as CLI 1, 2 and 3.
If you want to run the application using Apache Kafka as the message broker, then run the following commands on your respective CLIs -

CLI 1:
```
python3 producer_input.py Kafka
```
CLI 2:
```
python3 consumer_input_and_producer_output.py Kafka
```
CLI 3:
```
python3 consumer_output.py Kafka
```

If your choice of broker is Google Pub/Sub, take note of the name of the JSON file (for eg:'app_creds.json') and the Project ID as found in step 4, and run the following commands on your respective CLIs -

CLI 1:
```
python3 producer_input.py Google_Pub_Sub ${JSON file} ${Project ID}
```
CLI 2:
```
python3 consumer_input_and_producer_output.py Google_Pub_Sub ${JSON file} ${Project ID}
```
CLI 3:
```
python3 consumer_output.py Google_Pub_Sub ${JSON file} ${Project ID}
```

The CLI 1 command loads the test data from Fashion MNIST (10000 samples) and sends a serialized numpy array batch of 40 images every 5 seconds to the message broker of choice in the topic 'input-stream'.

The CLI 2 command consumes the data sent by the producer in CLI 1 in 'input-stream', and sends the data to the model for inference. This model is loaded from the file model.h5 that you can find in the project directory. It gives out a list of 40 results corresponding to the 40 input images sent at a time and this list is sent as a serialized object to the topic 'output-stream'.

The CLI 3 command consumes data incoming in the topic 'output-stream' and prints the same in the console. Theoretically a MongoDB instance can be initiated and the data incoming here can be sent to a collection in the database also.

**FUNCTIONAL FILES IN THE PROJECT :**

1. brokers.py - This file contains a class 'Broker' that would entail the major operations like initiating instances of producers and consumers on our choice of broker, or producing and consuming data from the initiated instances. This class has been used in the 3 main files - producer_input.py, consumer_input_and_producer_output.py and consumer_output.py

2. numpy_converters.py - To send numpy arrays in a seamless manner of JSON format using a message broker it was first required to create a class inherited from the JSONEncoder to support transport of these arrays. The two functions serialize and deserialize are used to create and deduce JSON readable objects of numpy arrays.

3. model_functions.py - It has basic model based functions to train a model and get predictions from a model saved at a particular path.

4. train_model.py - Can be used to train a new_model having the same architecture on a different dataset. Slight changes will have to be made to the code to load the new dataset into it. After making the changes, following command can be run to generate a new model from the command line after navigating to project folder -
```
python3 train_model.py ${epochs:int} ${model_name:str}
```
In order to test the newly created model on the data streaming application, rename it to model.h5 and you would be good to go.

**FEW KEY THINGS TO NOTE :**
1. While training the image classifier model I was able to get the accuracy up to 93% in the Google Colab Environment. I later tried training that model with the same data on my local MacOS machine and wasn't able to exceed 10% accuracy. I suspect this is happening because of some differences in how CPU and GPU perform but am not sure if that is the main reason for it. The model that I have uploaded here is the 93% accurate one.

2. As of now in this application the input and output streams have to be sent on the same broker in a single runtime. Surely slight tweaks in the code can give the flexibility of choosing different brokers for input and output streams as well.

3. It is important to select the check default subscription option in Google Pub/Sub as the code has been written in a manner to use the subscription named '${Topic}-sub' for any topic created in Google Pub/Sub. This dependency can also be eliminated if we use a database for managing topics and subscriptions at a large scale or maybe another algorithm for correlation between the topic and subscription names.

4. Security strengthening for the application can be done by restricting the IP list that the broker is allowed to consume data from and produce data to.

5. The Google Pub Sub consumer instances by default will deactive in 300 seconds. For keeping the code simple, I haven't parameterized this argument, but it is surely possible to do so.
