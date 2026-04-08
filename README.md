# 🤖 AI Image Classifier with Apache Kafka and Google Pub/Sub

A real-time image classification system that demonstrates how to integrate machine learning models with message brokers for scalable, distributed processing.

## 📑 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Setting up Apache Kafka](#setting-up-apache-kafka)
  - [Setting up Google Pub/Sub](#setting-up-google-pubsub)
- [Usage](#usage)
  - [Running with Kafka](#running-with-kafka)
  - [Running with Google Pub/Sub](#running-with-google-pubsub)
- [Project Structure](#project-structure)
- [Examples & Expected Output](#examples--expected-output)
- [Training Your Own Model](#training-your-own-model)
- [Troubleshooting](#troubleshooting)
- [Technical Notes](#technical-notes)
- [Contributing](#contributing)

## 🌟 Overview

This project demonstrates how to build a scalable machine learning pipeline using message brokers. It features:

- **Real-time image classification** using a CNN model trained on Fashion-MNIST dataset
- **Dual message broker support**: Apache Kafka and Google Pub/Sub
- **Streaming data pipeline** for continuous inference
- **Modular architecture** allowing easy integration of new brokers

### What are Message Brokers?

Message brokers are middleware that enable applications to communicate by sending messages through queues or topics:
- **Apache Kafka**: An open-source distributed streaming platform
- **Google Pub/Sub**: A fully-managed real-time messaging service by Google Cloud

### About Fashion-MNIST

Fashion-MNIST is a dataset of Zalando's article images consisting of 70,000 grayscale images in 10 categories (T-shirt, Trouser, Pullover, Dress, Coat, Sandal, Shirt, Sneaker, Bag, Ankle boot). Our CNN model achieves 93% accuracy on this dataset.

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Producer Input │ ──────▶ │  Message Broker │ ──────▶ │  Consumer &     │
│  (Fashion-MNIST │         │  (Kafka/PubSub) │         │  ML Inference   │
│   Test Data)    │         │  'input-stream' │         │                 │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                  │
                                                                  ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│ Consumer Output │ ◀────── │  Message Broker │ ◀────── │   Predictions   │
│  (Display/Store │         │  (Kafka/PubSub) │         │   (40 labels    │
│   Results)      │         │ 'output-stream' │         │    per batch)   │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.7+ | Runtime environment |
| Java | 8+ | Required for Apache Kafka |
| pip | Latest | Python package manager |

### Python Dependencies

```bash
tensorflow>=2.0.0
kafka-python
google-cloud-pubsub
numpy
```

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## 🚀 Installation

### Setting up Apache Kafka

1. **Download and Install Kafka**
   
   Follow the [official Kafka installation guide](https://www.tutorialspoint.com/apache_kafka/apache_kafka_installation_steps.htm) to install Kafka on your system.

2. **Start Zookeeper** (in Kafka directory)
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

3. **Start Kafka Server** (in a new terminal)
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```

4. **Create Required Topics**
   ```bash
   # Create input stream topic
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
     --topic input-stream --partitions 1 --replication-factor 1
   
   # Create output stream topic
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
     --topic output-stream --partitions 1 --replication-factor 1
   ```

   💡 **Tip**: If Kafka is not on localhost:9092, adjust the `--bootstrap-server` parameter accordingly.

### Setting up Google Pub/Sub

1. **Create a GCP Service Account**
   - Go to [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Click "Create Service Account"
   - Name your account (e.g., `ml-pipeline-service`)
   - Grant these roles:
     - `Pub/Sub Publisher`
     - `Pub/Sub Subscriber`

2. **Generate Private Key**
   - Find your service account and click "Manage keys"
   - Click "Add Key" → "Create new key"
   - Choose JSON format
   - Save the downloaded file in your project directory (e.g., `app_creds.json`)

3. **Create Pub/Sub Topics**
   - Go to [Pub/Sub Topics](https://console.cloud.google.com/cloudpubsub/topic/list)
   - Create two topics:
     - `input-stream` (✅ Keep default subscription checked)
     - `output-stream` (✅ Keep default subscription checked)
   - Note your Project ID from the URL: `projects/{PROJECT_ID}/topics/...`

## 💻 Usage

You'll need three terminal windows to run the complete pipeline:

### Running with Kafka

**Terminal 1 - Producer** (Sends image data)
```bash
python3 producer_input.py Kafka
```

**Terminal 2 - ML Pipeline** (Processes images and generates predictions)
```bash
python3 consumer_input_and_producer_output.py Kafka
```

**Terminal 3 - Consumer** (Displays results)
```bash
python3 consumer_output.py Kafka
```

### Running with Google Pub/Sub

Replace `{JSON_FILE}` with your credentials file name and `{PROJECT_ID}` with your GCP project ID:

**Terminal 1 - Producer**
```bash
python3 producer_input.py Google_Pub_Sub app_creds.json your-project-id
```

**Terminal 2 - ML Pipeline**
```bash
python3 consumer_input_and_producer_output.py Google_Pub_Sub app_creds.json your-project-id
```

**Terminal 3 - Consumer**
```bash
python3 consumer_output.py Google_Pub_Sub app_creds.json your-project-id
```

## 📁 Project Structure

| File | Description |
|------|-------------|
| `brokers.py` | Broker abstraction class handling Kafka/Pub/Sub operations |
| `producer_input.py` | Loads Fashion-MNIST test data and streams batches of 40 images |
| `consumer_input_and_producer_output.py` | Consumes images, runs inference, publishes predictions |
| `consumer_output.py` | Consumes and displays prediction results |
| `model.h5` | Pre-trained CNN model (93% accuracy) |
| `model_functions.py` | Model training and prediction utilities |
| `numpy_converters.py` | JSON serialization for numpy arrays |
| `train_model.py` | Script to train new models |
| `requirements.txt` | Python dependencies |

## 📊 Examples & Expected Output

### Producer Input Output
```
Producing batch 1 of 250...
Sent 40 images to input-stream
Producing batch 2 of 250...
Sent 40 images to input-stream
...
```

### ML Pipeline Output
```
Loaded model from model.h5
Consuming from input-stream...
Received batch of 40 images
Predictions: [2, 1, 0, 9, 1, 1, 6, 1, 4, 6, ...]
Sent predictions to output-stream
...
```

### Consumer Output
```
Consuming from output-stream...
Received predictions: 
- Image 1: Class 2 (Pullover)
- Image 2: Class 1 (Trouser)
- Image 3: Class 0 (T-shirt/top)
- Image 4: Class 9 (Ankle boot)
...
```

### Fashion-MNIST Classes
| Label | Description |
|-------|-------------|
| 0 | T-shirt/top |
| 1 | Trouser |
| 2 | Pullover |
| 3 | Dress |
| 4 | Coat |
| 5 | Sandal |
| 6 | Shirt |
| 7 | Sneaker |
| 8 | Bag |
| 9 | Ankle boot |

## 🏋️ Training Your Own Model

To train a new model with different parameters:

```bash
python3 train_model.py {epochs} {model_name}
# Example: python3 train_model.py 20 my_fashion_model
```

To use your custom model:
1. Rename it to `model.h5`
2. Place it in the project directory
3. Run the pipeline as usual

⚠️ **Note**: Ensure your model architecture matches the expected input shape (28x28x1).

## 🔧 Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| **Kafka connection refused** | Ensure Kafka and Zookeeper are running |
| **Google Pub/Sub authentication error** | Check if JSON credentials file path is correct |
| **Model accuracy is low** | The included model was trained on GPU; CPU training may yield different results |
| **Consumer timeout** | Kafka consumers timeout after 90s of inactivity; Pub/Sub after 300s |
| **Topic not found** | Ensure topics are created before running the scripts |

### Debugging Tips

1. **Check Kafka topics:**
   ```bash
   bin/kafka-topics.sh --list --bootstrap-server localhost:9092
   ```

2. **Monitor Kafka consumer groups:**
   ```bash
   bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
   ```

3. **Test Google Pub/Sub connection:**
   ```python
   from google.cloud import pubsub_v1
   # This should not throw an error if credentials are correct
   ```

## 🔍 Technical Notes

### Key Design Decisions

1. **Batch Size**: 40 images per batch balances throughput and latency
2. **Serialization**: Custom JSON encoder handles numpy arrays efficiently
3. **Broker Abstraction**: `Broker` class enables easy addition of new message brokers
4. **Model Format**: H5 format for TensorFlow/Keras compatibility

### Performance Considerations

- The pipeline processes ~8 images per second (40 images every 5 seconds)
- Kafka provides better throughput for local deployments
- Pub/Sub offers better scalability for cloud deployments
- Model inference is the primary bottleneck; consider GPU for production

### Security Best Practices

- Store credentials in environment variables, not in code
- Restrict service account permissions to minimum required
- Use SSL/TLS for Kafka in production
- Implement IP whitelisting for broker access

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Improvement

- [ ] Add support for more message brokers (RabbitMQ, Redis)
- [ ] Implement model versioning
- [ ] Add real-time performance monitoring
- [ ] Create Docker containers for easy deployment
- [ ] Add unit tests
- [ ] Support for different ML frameworks

---

**License**: This project is open source and available under the [MIT License](LICENSE).

**Author**: Aditya Shrivastava

**Questions?** Feel free to open an issue or reach out!