# Image Classifier Integrated with Apache Kafka and Google Pub/Sub

A distributed machine learning system that demonstrates real-time image classification using message brokers (Apache Kafka or Google Pub/Sub) for scalable data streaming. The system processes Fashion MNIST images through a CNN model with a publish-subscribe architecture.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Apache Kafka Setup](#apache-kafka-setup)
  - [Google Pub/Sub Setup](#google-pubsub-setup)
- [Quick Usage Examples](#quick-usage-examples)
  - [Using Apache Kafka](#using-apache-kafka)
  - [Using Google Pub/Sub](#using-google-pubsub)
- [Project Components](#project-components)
- [Key Implementation Details](#key-implementation-details)
- [Customization](#customization)

## Overview

This project demonstrates how to integrate machine learning models with message brokers for scalable, real-time inference. Key features include:

- **Dual Broker Support**: Seamlessly switch between Apache Kafka and Google Pub/Sub
- **Real-time Processing**: Stream image batches through message queues for continuous inference
- **CNN Classifier**: Pre-trained model achieving 93% accuracy on Fashion MNIST dataset
- **Modular Design**: Abstract broker interface allows easy addition of new message brokers
- **Batch Processing**: Efficiently processes 40 images per batch every 5 seconds

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│                 │     │                  │     │                     │
│  Producer Input │────▶│  Message Broker  │────▶│ Consumer Input &    │
│                 │     │  (input-stream)  │     │ Producer Output     │
│ - Loads Fashion│     │                  │     │                     │
│   MNIST test   │     │ - Apache Kafka   │     │ - Consumes batches  │
│   data (10k    │     │      OR          │     │ - Runs CNN          │
│   samples)     │     │ - Google Pub/Sub │     │   inference         │
│ - Sends 40     │     │                  │     │ - Publishes results │
│   image batches│     └──────────────────┘     │                     │
│   every 5 sec  │                              └──────────┬──────────┘
└─────────────────┘                                        │
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│                 │     │                  │     │                  │
│ Consumer Output │◀────│  Message Broker  │◀────┘  CNN Model       │
│                 │     │  (output-stream) │     │  (model.h5)      │
│ - Receives      │     │                  │     │                  │
│   predictions  │     │ - Apache Kafka   │     │ - Conv2D layers  │
│ - Displays      │     │      OR          │     │ - MaxPooling     │
│   results      │     │ - Google Pub/Sub │     │ - Dense layers   │
│ - Can store    │     │                  │     │ - 10 categories  │
│   to MongoDB   │     └──────────────────┘     └──────────────────┘
└─────────────────┘
```

### Data Flow

1. **Producer Input**: Loads Fashion MNIST test data and publishes serialized numpy arrays (40 images/batch) to the input stream
2. **Message Broker**: Routes messages between producers and consumers using either Kafka or Pub/Sub
3. **Consumer/Producer**: Consumes input batches, performs inference, and publishes predictions to output stream
4. **Consumer Output**: Receives and displays classification results (can be extended to store in MongoDB)

## Prerequisites

- Python 3.6+
- For Apache Kafka:
  - Java 8+
  - Apache Kafka 2.x
  - Zookeeper (included with Kafka)
- For Google Pub/Sub:
  - Google Cloud Platform account
  - Service account with Pub/Sub Publisher/Subscriber roles
  - Project ID

## Installation

### Apache Kafka Setup

1. **Install and Start Kafka**
   
   Follow the [official Kafka installation guide](https://www.tutorialspoint.com/apache_kafka/apache_kafka_installation_steps.htm) to set up Zookeeper and Kafka.

2. **Create Kafka Topics**
   
   Navigate to your Kafka directory and run:
   ```bash
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic input-stream --partitions 1 --replication-factor 1
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic output-stream --partitions 1 --replication-factor 1
   ```

### Google Pub/Sub Setup

1. **Create Service Account**
   - Go to [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Click "Create Service Account"
   - Add roles: Pub/Sub Publisher and Pub/Sub Subscriber
   
2. **Generate Private Key**
   - Select your service account → Manage keys → Add key → Create new key (JSON)
   - Save the downloaded JSON file in your project directory

3. **Create Pub/Sub Topics**
   - Visit [Pub/Sub Topics](https://console.cloud.google.com/cloudpubsub/topic/list)
   - Create topics: `input-stream` and `output-stream`
   - **Important**: Keep "Add a default subscription" checked
   - Note your Project ID from the URL: `projects/{Project-ID}/topics/...`

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Usage Examples

### Using Apache Kafka

Open three terminal windows and navigate to the project directory in each:

**Terminal 1 - Start Producer**
```bash
python3 producer_input.py Kafka
```

**Terminal 2 - Start Consumer/Producer**
```bash
python3 consumer_input_and_producer_output.py Kafka
```

**Terminal 3 - Start Output Consumer**
```bash
python3 consumer_output.py Kafka
```

### Using Google Pub/Sub

Replace `your-creds.json` and `your-project-id` with your actual values:

**Terminal 1 - Start Producer**
```bash
python3 producer_input.py Google_Pub_Sub your-creds.json your-project-id
```

**Terminal 2 - Start Consumer/Producer**
```bash
python3 consumer_input_and_producer_output.py Google_Pub_Sub your-creds.json your-project-id
```

**Terminal 3 - Start Output Consumer**
```bash
python3 consumer_output.py Google_Pub_Sub your-creds.json your-project-id
```

### Expected Output

Once all three components are running, you should see:
- Producer: Sending batch messages every 5 seconds
- Consumer/Producer: Processing batches and generating predictions
- Output Consumer: Displaying classification results for each batch

Example output:
```
Received predictions: [2, 4, 1, 9, 0, 1, 7, 8, 5, 3, ...]
```

## Project Components

| File | Description |
|------|-------------|
| `brokers.py` | Abstract `Broker` class providing unified interface for Kafka and Pub/Sub operations |
| `producer_input.py` | Loads Fashion MNIST data and publishes image batches to input stream |
| `consumer_input_and_producer_output.py` | Consumes images, runs inference, publishes predictions |
| `consumer_output.py` | Consumes and displays prediction results |
| `model_functions.py` | Model building and training utilities |
| `numpy_converters.py` | JSON serialization/deserialization for numpy arrays |
| `train_model.py` | Script to retrain the CNN model |
| `model.h5` | Pre-trained CNN model (93% accuracy) |

## Key Implementation Details

1. **Broker Abstraction**: The `Broker` class in `brokers.py` provides a unified interface for both Kafka and Google Pub/Sub, making it easy to switch between brokers or add new ones.

2. **Batch Processing**: The system processes 40 images per batch to optimize throughput while maintaining reasonable latency.

3. **Model Architecture**: CNN with 2 Conv2D layers, MaxPooling, and Dense layers trained on Fashion MNIST (28x28 grayscale images, 10 categories).

4. **Serialization**: Custom JSON encoder/decoder handles numpy array serialization for message passing.

5. **Timeout Configuration**: 
   - Google Pub/Sub consumers: 300 seconds timeout
   - Kafka consumers: 90 seconds idle timeout

## Customization

### Training a New Model

To train the model on a different dataset:

```bash
python3 train_model.py <epochs> <model_name>
```

Example:
```bash
python3 train_model.py 10 my_custom_model
```

To use your custom model, rename it to `model.h5` in the project directory.

### Adding a New Message Broker

1. Extend the `Broker` class in `brokers.py`
2. Implement the required methods: `create_producer()`, `create_consumer()`, `produce()`, `consume()`
3. Add broker initialization logic in the main scripts

### Security Considerations

- Restrict broker access by IP whitelisting
- Use SSL/TLS for Kafka connections in production
- Rotate Google Cloud service account keys regularly
- Never commit credentials to version control

---

**Note**: The model was trained on Google Colab with GPU acceleration achieving 93% accuracy. Training on CPU-only systems may yield different results due to numerical precision differences.