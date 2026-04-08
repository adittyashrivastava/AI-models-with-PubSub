# 🤖 Real-time Image Classification with Message Brokers

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.3.1-orange.svg)](https://www.tensorflow.org/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-Supported-black.svg)](https://kafka.apache.org/)
[![Google Pub/Sub](https://img.shields.io/badge/Google%20Pub%2FSub-Supported-blue.svg)](https://cloud.google.com/pubsub)

A production-ready implementation of distributed image classification using Apache Kafka and Google Pub/Sub message brokers. This project demonstrates how to build scalable ML pipelines with real-time data streaming capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Apache Kafka Setup](#apache-kafka-setup)
  - [Google Pub/Sub Setup](#google-pubsub-setup)
- [Usage](#usage)
  - [Running with Kafka](#running-with-kafka)
  - [Running with Google Pub/Sub](#running-with-google-pubsub)
- [Project Structure](#project-structure)
- [Model Performance](#model-performance)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project implements a distributed image classification system that:
- Processes Fashion MNIST images in real-time
- Supports both Apache Kafka and Google Pub/Sub as message brokers
- Achieves 93% accuracy on Fashion MNIST dataset
- Provides seamless broker switching through abstraction layer
- Enables scalable, microservices-based ML deployment

## 🏗️ Architecture

```
┌──────────────┐      ┌─────────────────┐      ┌───────────────┐
│   Producer   │      │  Message Broker │      │   Consumer    │
│    Input     │─────►│  (Kafka/PubSub) │─────►│  ML Inference │
└──────────────┘      └─────────────────┘      └───────┬───────┘
                                                        │
                      ┌─────────────────┐               │
                      │  Message Broker │◄──────────────┘
                      │  (Kafka/PubSub) │
                      └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │    Consumer     │
                      │     Output      │
                      └─────────────────┘
```

### Data Flow

1. **Producer Input**: Loads Fashion MNIST test data and streams batches of 40 images every 5 seconds
2. **Consumer/Producer**: Consumes images, performs inference, and publishes predictions
3. **Consumer Output**: Receives and displays classification results

## ✨ Features

- **Multi-Broker Support**: Seamlessly switch between Apache Kafka and Google Pub/Sub
- **Real-time Processing**: Stream and process images in batches of 40
- **High Accuracy**: Pre-trained CNN model with 93% accuracy on Fashion MNIST
- **Scalable Architecture**: Microservices-based design for easy scaling
- **Custom Serialization**: Efficient numpy array serialization for message transport
- **Extensible Design**: Easy to adapt for different datasets and models

## 📚 Prerequisites

### Software Requirements

- Python 3.7+
- Apache Kafka (optional, if using Kafka)
- Google Cloud account with Pub/Sub enabled (optional, if using Pub/Sub)
- pip package manager

### Python Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

Dependencies include:
- `tensorflow==2.3.1`
- `kafka-python==2.0.2`
- `google-cloud-pubsub==2.9.0`
- `numpy==1.18.1`
- And more (see requirements.txt)

## 🚀 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/adittyashrivastava/AI-models-with-PubSub.git
   cd AI-models-with-PubSub
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose Your Message Broker**
   - For Kafka: Follow [Apache Kafka Setup](#apache-kafka-setup)
   - For Google Pub/Sub: Follow [Google Pub/Sub Setup](#google-pubsub-setup)

## ⚙️ Configuration

### Apache Kafka Setup

1. **Install and Start Kafka**
   
   Follow the [official Kafka installation guide](https://www.tutorialspoint.com/apache_kafka/apache_kafka_installation_steps.htm).

2. **Start Zookeeper**
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

3. **Start Kafka Server**
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```

4. **Create Required Topics**
   ```bash
   # Navigate to your Kafka directory
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
     --topic input-stream --partitions 1 --replication-factor 1
   
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
     --topic output-stream --partitions 1 --replication-factor 1
   ```

### Google Pub/Sub Setup

1. **Create a GCP Service Account**
   
   - Go to [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Click "Create Service Account"
   - Provide a name and unique ID
   - Add roles: `Pub/Sub Publisher` and `Pub/Sub Subscriber`

2. **Generate Private Key**
   
   - Find your service account and click "Manage Keys"
   - Click "Add Key" → "Create new key"
   - Choose JSON format
   - Save the downloaded file in the project directory

3. **Create Pub/Sub Topics**
   
   - Go to [Pub/Sub Topics page](https://console.cloud.google.com/cloudpubsub/topic/list)
   - Create topics: `input-stream` and `output-stream`
   - **Important**: Keep the default subscription option checked
   
4. **Note Your Project ID**
   
   Find it on the Pub/Sub page: `projects/{PROJECT_ID}/topics/...`

## 🎮 Usage

Open three terminal windows and navigate to the project directory in each.

### Running with Kafka

**Terminal 1 - Producer Input:**
```bash
python3 producer_input.py Kafka
```

**Terminal 2 - ML Inference Pipeline:**
```bash
python3 consumer_input_and_producer_output.py Kafka
```

**Terminal 3 - Consumer Output:**
```bash
python3 consumer_output.py Kafka
```

### Running with Google Pub/Sub

**Terminal 1 - Producer Input:**
```bash
python3 producer_input.py Google_Pub_Sub <JSON_FILE> <PROJECT_ID>
```

**Terminal 2 - ML Inference Pipeline:**
```bash
python3 consumer_input_and_producer_output.py Google_Pub_Sub <JSON_FILE> <PROJECT_ID>
```

**Terminal 3 - Consumer Output:**
```bash
python3 consumer_output.py Google_Pub_Sub <JSON_FILE> <PROJECT_ID>
```

**Example:**
```bash
python3 producer_input.py Google_Pub_Sub app_creds.json my-project-123
```

## 📁 Project Structure

```
AI-models-with-PubSub/
├── README.md                                  # This file
├── requirements.txt                           # Python dependencies
├── model.h5                                   # Pre-trained CNN model (93% accuracy)
├── brokers.py                                # Broker abstraction layer
├── producer_input.py                         # Streams Fashion MNIST images
├── consumer_input_and_producer_output.py     # ML inference pipeline
├── consumer_output.py                        # Displays predictions
├── numpy_converters.py                       # Numpy array serialization
├── model_functions.py                        # Model training/prediction utilities
└── train_model.py                           # Script to train new models
```

### Key Files Explained

- **`brokers.py`**: Unified interface for Kafka and Pub/Sub operations
- **`numpy_converters.py`**: Custom JSON encoder/decoder for numpy arrays
- **`model_functions.py`**: Helper functions for model operations
- **`train_model.py`**: Training script for creating new models

## 📊 Model Performance

- **Dataset**: Fashion MNIST (10 classes of clothing items)
- **Architecture**: CNN (Convolutional Neural Network)
- **Accuracy**: 93% on test set
- **Batch Size**: 40 images
- **Processing Rate**: 1 batch every 5 seconds

> **Note**: The model was trained on Google Colab with GPU acceleration. Training on CPU may yield different results.

## 🔧 Customization

### Training a New Model

To train a model with custom parameters:

```bash
python3 train_model.py <EPOCHS> <MODEL_NAME>
```

**Example:**
```bash
python3 train_model.py 50 my_custom_model
```

To use your custom model:
1. Rename it to `model.h5`
2. Replace the existing model file
3. Run the application as usual

### Modifying for Different Datasets

1. Update `train_model.py` to load your dataset
2. Adjust model architecture in `model_functions.py` if needed
3. Update batch size and timing in producer/consumer scripts

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Error**
   - Ensure Kafka and Zookeeper are running
   - Check if topics are created correctly
   - Verify `localhost:9092` is the correct broker address

2. **Google Pub/Sub Authentication Error**
   - Verify JSON credentials file exists and path is correct
   - Check service account has required permissions
   - Ensure Project ID is correct

3. **Model Accuracy Issues**
   - The included model was trained on GPU
   - CPU training may yield different results
   - Consider retraining on your specific hardware

4. **Consumer Timeout**
   - Kafka consumers timeout after 90 seconds of inactivity
   - Google Pub/Sub consumers timeout after 300 seconds
   - Keep producers running to avoid timeouts

### Performance Considerations

- **Batch Size**: Adjust batch size based on your system's capabilities
- **Processing Interval**: Modify the 5-second interval in `producer_input.py` as needed
- **Network Latency**: Consider network delays when using cloud-based brokers

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Author**: Adittya Shrivastava  
**Contact**: [GitHub Profile](https://github.com/adittyashrivastava)

## 🚀 Future Enhancements

- [ ] Support for multiple image formats (JPEG, PNG, etc.)
- [ ] Web UI for real-time monitoring
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests
- [ ] Support for additional message brokers (RabbitMQ, Redis Streams)
- [ ] Model versioning and A/B testing capabilities
- [ ] Metrics and monitoring integration (Prometheus, Grafana)
