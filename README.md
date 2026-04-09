# Image Classifier with Real-time Streaming using Apache Kafka and Google Pub/Sub

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.3.1-orange.svg)
![Kafka](https://img.shields.io/badge/kafka-compatible-green.svg)
![Google Cloud](https://img.shields.io/badge/google--cloud-pubsub-blue.svg)

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Key Components](#key-components)
- [Setup Instructions](#setup-instructions)
  - [Apache Kafka Setup](#apache-kafka-setup)
  - [Google Pub/Sub Setup](#google-pubsub-setup)
- [Usage](#usage)
  - [Running with Apache Kafka](#running-with-apache-kafka)
  - [Running with Google Pub/Sub](#running-with-google-pubsub)
- [Project Files](#project-files)
- [Important Notes](#important-notes)

## Overview

This project demonstrates a real-time machine learning inference pipeline that integrates AI models with message brokers (Apache Kafka and Google Pub/Sub). It showcases how to build a scalable, distributed system for processing image data streams in real-time using a CNN-based image classifier trained on the Fashion MNIST dataset.

### What does this project do?
- **Streams image data** through message brokers for real-time processing
- **Performs ML inference** on batches of images using a pre-trained CNN model
- **Supports multiple message brokers** with a unified interface (Kafka and Google Pub/Sub)
- **Demonstrates microservices architecture** with separate producer, consumer, and ML components

### Key Features
- ✅ Real-time image classification with 93% accuracy
- ✅ Batch processing of 40 images every 5 seconds
- ✅ Broker-agnostic design for easy switching between Kafka and Pub/Sub
- ✅ Modular architecture for easy extension and modification
- ✅ Pre-trained Fashion MNIST classifier included

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          Real-time ML Inference Pipeline                         │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │                 │         │                 │         │                 │
    │  Producer Input │         │ Message Broker  │         │ Consumer Input  │
    │                 │         │                 │         │       +         │
    │ Loads Fashion   │ ──────▶ │ Apache Kafka    │ ──────▶ │   ML Model      │
    │ MNIST Test Data │         │      OR         │         │                 │
    │ (10,000 images) │         │ Google Pub/Sub  │         │ CNN Classifier  │
    │                 │         │                 │         │ (93% accuracy)  │
    └─────────────────┘         └─────────────────┘         └────────┬────────┘
           CLI 1                  Topic: input-stream                │
                                                                     │
                                                              Predictions
                                                                     │
                                                                     ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │                 │         │                 │         │                 │
    │ Consumer Output │         │ Message Broker  │         │ Producer Output │
    │                 │         │                 │         │                 │
    │ Displays Results│ ◀────── │ Apache Kafka    │ ◀────── │ Sends Model     │
    │ in Console      │         │      OR         │         │ Predictions     │
    │                 │         │ Google Pub/Sub  │         │                 │
    └─────────────────┘         └─────────────────┘         └─────────────────┘
           CLI 3                  Topic: output-stream               CLI 2

Data Flow:
1. Producer loads batches of 40 Fashion MNIST images
2. Images are serialized and sent to 'input-stream' topic
3. Consumer receives images, performs inference using CNN model
4. Predictions are sent to 'output-stream' topic
5. Final consumer displays results (can be extended to save to database)
```

## Key Components

### 1. **Message Brokers Layer**
   - **Apache Kafka**: High-throughput distributed streaming platform
   - **Google Pub/Sub**: Fully managed real-time messaging service
   - Unified `Broker` class interface for seamless switching between brokers

### 2. **Data Pipeline Components**
   - **Producer Input**: Loads Fashion MNIST test data and streams batches of 40 images
   - **Consumer/ML Model**: Receives images, performs inference, outputs predictions
   - **Consumer Output**: Receives and displays classification results

### 3. **ML Model**
   - Pre-trained CNN classifier for Fashion MNIST dataset
   - 93% accuracy on test data
   - Processes batches of 40 images for efficient inference

### 4. **Utilities**
   - **Numpy Converters**: Serialization/deserialization for numpy arrays
   - **Model Functions**: Training and prediction utilities

## Setup Instructions

### Prerequisites
- Python 3.x
- pip package manager
- (For Kafka) Java 8 or higher
- (For Google Pub/Sub) Google Cloud Platform account

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Apache Kafka Setup

**STEP 1:** Install and start Zookeeper and Kafka on localhost. Follow the installation guide [here](https://www.tutorialspoint.com/apache_kafka/apache_kafka_installation_steps.htm).

**STEP 2:** Create Kafka topics by navigating to your Kafka directory and running:
```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic input-stream --partitions 1 --replication-factor 1
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic output-stream --partitions 1 --replication-factor 1
```

### Google Pub/Sub Setup

**STEP 1:** Create a GCP Service Account
- Access your service accounts [here](https://console.cloud.google.com/iam-admin/serviceaccounts)
- Create a new account [here](https://console.cloud.google.com/iam-admin/serviceaccounts/create)
- Add Pub/Sub Publisher and Subscriber roles

**STEP 2:** Generate Private Key
- Find your service account and select "Manage keys"
- Add a new JSON key and download it
- Place the JSON file in your project folder

**STEP 3:** Create Pub/Sub Topics
- View topics [here](https://console.cloud.google.com/cloudpubsub/topic/list)
- Create topics named 'input-stream' and 'output-stream'
- Keep the default subscription option checked (creates '{topic-name}-sub')
- Note your Project ID from the topics list page

## Usage

Open three terminal windows and navigate to the project directory in each.

### Running with Apache Kafka

Terminal 1 - Start Producer:
```bash
python3 producer_input.py Kafka
```

Terminal 2 - Start Consumer/ML Model:
```bash
python3 consumer_input_and_producer_output.py Kafka
```

Terminal 3 - Start Output Consumer:
```bash
python3 consumer_output.py Kafka
```

### Running with Google Pub/Sub

Terminal 1 - Start Producer:
```bash
python3 producer_input.py Google_Pub_Sub ${JSON_FILE} ${PROJECT_ID}
```

Terminal 2 - Start Consumer/ML Model:
```bash
python3 consumer_input_and_producer_output.py Google_Pub_Sub ${JSON_FILE} ${PROJECT_ID}
```

Terminal 3 - Start Output Consumer:
```bash
python3 consumer_output.py Google_Pub_Sub ${JSON_FILE} ${PROJECT_ID}
```

Replace `${JSON_FILE}` with your credentials file name (e.g., 'app_creds.json') and `${PROJECT_ID}` with your GCP project ID.

## Project Files

- **`brokers.py`**: Unified Broker class for Kafka and Pub/Sub operations
- **`numpy_converters.py`**: JSON serialization for numpy arrays
- **`model_functions.py`**: Model training and prediction utilities
- **`train_model.py`**: Script to train new models
- **`producer_input.py`**: Streams Fashion MNIST images to message broker
- **`consumer_input_and_producer_output.py`**: Performs ML inference
- **`consumer_output.py`**: Displays classification results
- **`model.h5`**: Pre-trained CNN model (93% accuracy)
- **`requirements.txt`**: Python dependencies

### Training a New Model
```bash
python3 train_model.py ${epochs:int} ${model_name:str}
```
To use a new model, rename it to `model.h5`.

## Important Notes

1. **Model Performance**: The included model achieves 93% accuracy when trained on GPU (Google Colab). CPU training may yield different results due to computational differences.

2. **Broker Consistency**: Currently, input and output streams must use the same broker in a single runtime. This can be modified for mixed-broker scenarios.

3. **Subscription Naming**: Google Pub/Sub code expects subscriptions named `${topic}-sub`. Ensure default subscriptions are created when making topics.

4. **Timeout Settings**: 
   - Google Pub/Sub consumers: 300 seconds timeout
   - Kafka consumers: 90 seconds inactivity timeout

5. **Security**: Consider implementing IP restrictions for production deployments.

6. **Extensibility**: The consumer output can be extended to save results to MongoDB or other databases.