# Low-Level Design Documentation

## Overview

This document describes the improved object-oriented design of the AI-models-with-PubSub system. The refactoring introduces proper class hierarchies for producers, consumers, and serializers, making the codebase more maintainable and extensible.

## Architecture Components

### 1. Serializers (`serializers.py`)

Abstract base class and concrete implementations for data serialization:

- **`Serializer`** (Abstract Base Class)
  - Defines the interface for all serializers
  - Methods: `serialize()`, `deserialize()`

- **`NumpySerializer`**
  - Handles serialization of numpy arrays
  - Converts arrays to JSON-serializable lists

- **`JSONSerializer`**
  - Handles standard JSON data (dicts, lists)
  - Default serializer for most use cases

### 2. Messaging Components (`messaging.py`)

Abstract base classes and concrete implementations for message passing:

#### Base Classes

- **`Producer`** (Abstract Base Class)
  - Defines interface for all producers
  - Methods: `send()`, `close()`
  - Handles topic and serializer configuration

- **`Consumer`** (Abstract Base Class)
  - Defines interface for all consumers
  - Methods: `consume()`, `close()`
  - Handles topic and serializer configuration

#### Concrete Implementations

- **`KafkaProducer`**
  - Kafka-specific producer implementation
  - Configures Kafka client with serializer

- **`KafkaConsumer`**
  - Kafka-specific consumer implementation
  - Supports message consumption with callbacks

- **`GooglePubSubProducer`**
  - Google Pub/Sub producer implementation
  - Handles project and topic path configuration

- **`GooglePubSubConsumer`**
  - Google Pub/Sub consumer implementation
  - Manages subscriptions and message acknowledgment

#### Factory Functions

- `create_producer()` - Creates appropriate producer based on broker type
- `create_consumer()` - Creates appropriate consumer based on broker type

### 3. Broker Management (`brokers.py`)

- **`Broker`**
  - Main entry point for creating producers and consumers
  - Handles environment variable configuration
  - Methods:
    - `get_producer()` - Returns configured producer instance
    - `get_consumer()` - Returns configured consumer instance
  - Properties:
    - `is_kafka` - Check if using Kafka
    - `is_pubsub` - Check if using Google Pub/Sub

## Usage Examples

### Creating a Producer

```python
from brokers import Broker
from serializers import NumpySerializer

# Initialize broker
broker = Broker()  # Uses BROKER_TYPE env var

# Get producer with numpy serializer
producer = broker.get_producer('my-topic', serializer=NumpySerializer())

# Send data
producer.send(numpy_array)
producer.close()
```

### Creating a Consumer

```python
from brokers import Broker
from serializers import NumpySerializer

# Initialize broker
broker = Broker()

# Get consumer with numpy serializer
consumer = broker.get_consumer('my-topic', serializer=NumpySerializer())

# Define callback
def process_message(data):
    print(f"Received: {data}")

# Start consuming
consumer.consume(process_message)
consumer.close()
```

## Benefits of the New Design

1. **Separation of Concerns**: Each class has a single, well-defined responsibility
2. **Extensibility**: Easy to add new broker types or serializers
3. **Type Safety**: Abstract base classes ensure consistent interfaces
4. **Testability**: Components can be easily mocked for unit testing
5. **Configuration Management**: Centralized configuration through Broker class
6. **Error Handling**: Consistent error handling across implementations

## Environment Variables

- `BROKER_TYPE`: 'kafka' or 'pubsub' (default: 'kafka')
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka server address (default: 'localhost:9092')
- `KAFKA_GROUP_ID`: Consumer group ID (default: 'default-group')
- `GOOGLE_CLOUD_PROJECT`: GCP project ID for Pub/Sub
- `PUBSUB_SUBSCRIPTION`: Subscription name for Pub/Sub consumer
- `INPUT_TOPIC`: Topic for input messages
- `OUTPUT_TOPIC`: Topic for output messages

## Migration from Old Design

The old design used:
- Direct broker object manipulation
- Standalone functions in `numpy_converters.py`
- Mixed responsibilities in scripts

The new design provides:
- Clean abstraction layers
- Object-oriented approach
- Clear separation of messaging, serialization, and business logic
