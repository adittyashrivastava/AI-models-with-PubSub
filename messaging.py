"""
Abstract base classes and implementations for message producers and consumers
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Dict
from kafka import KafkaProducer as KafkaProducerClient, KafkaConsumer as KafkaConsumerClient
from google.cloud import pubsub_v1
from google.api_core import retry
from concurrent.futures import TimeoutError
import os
import logging

from serializers import Serializer, NumpySerializer, JSONSerializer


class Producer(ABC):
    """Abstract base class for message producers"""
    
    def __init__(self, topic: str, serializer: Optional[Serializer] = None):
        self.topic = topic
        self.serializer = serializer or JSONSerializer()
        
    @abstractmethod
    def send(self, data: Any, key: Optional[str] = None) -> None:
        """Send data to the topic"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the producer connection"""
        pass


class Consumer(ABC):
    """Abstract base class for message consumers"""
    
    def __init__(self, topic: str, serializer: Optional[Serializer] = None):
        self.topic = topic
        self.serializer = serializer or JSONSerializer()
        
    @abstractmethod
    def consume(self, callback: Callable[[Any], None], **kwargs) -> None:
        """
        Consume messages from the topic
        
        Args:
            callback: Function to call with each message
            **kwargs: Additional arguments for the consumer
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the consumer connection"""
        pass


class KafkaProducer(Producer):
    """Kafka implementation of Producer"""
    
    def __init__(self, topic: str, bootstrap_servers: str = 'localhost:9092', 
                 serializer: Optional[Serializer] = None, **kafka_config):
        super().__init__(topic, serializer)
        self.producer = KafkaProducerClient(
            bootstrap_servers=bootstrap_servers,
            value_serializer=self.serializer.serialize,
            **kafka_config
        )
        
    def send(self, data: Any, key: Optional[str] = None) -> None:
        """Send data to Kafka topic"""
        try:
            if key:
                self.producer.send(self.topic, key=key.encode('utf-8'), value=data)
            else:
                self.producer.send(self.topic, value=data)
            self.producer.flush()
        except Exception as e:
            logging.error(f"Error sending message to Kafka: {e}")
            raise
            
    def close(self) -> None:
        """Close Kafka producer"""
        self.producer.close()


class KafkaConsumer(Consumer):
    """Kafka implementation of Consumer"""
    
    def __init__(self, topic: str, bootstrap_servers: str = 'localhost:9092',
                 group_id: str = 'my-group', serializer: Optional[Serializer] = None, 
                 **kafka_config):
        super().__init__(topic, serializer)
        self.consumer = KafkaConsumerClient(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=self.serializer.deserialize,
            **kafka_config
        )
        
    def consume(self, callback: Callable[[Any], None], max_messages: Optional[int] = None) -> None:
        """Consume messages from Kafka topic"""
        try:
            message_count = 0
            for message in self.consumer:
                callback(message.value)
                message_count += 1
                if max_messages and message_count >= max_messages:
                    break
        except Exception as e:
            logging.error(f"Error consuming messages from Kafka: {e}")
            raise
            
    def close(self) -> None:
        """Close Kafka consumer"""
        self.consumer.close()


class GooglePubSubProducer(Producer):
    """Google Pub/Sub implementation of Producer"""
    
    def __init__(self, topic: str, project_id: str, serializer: Optional[Serializer] = None):
        super().__init__(topic, serializer)
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic)
        
    def send(self, data: Any, key: Optional[str] = None) -> None:
        """Send data to Google Pub/Sub topic"""
        try:
            message_data = self.serializer.serialize(data)
            attributes = {'key': key} if key else {}
            future = self.publisher.publish(self.topic_path, message_data, **attributes)
            # Wait for the publish to complete
            future.result()
        except Exception as e:
            logging.error(f"Error sending message to Pub/Sub: {e}")
            raise
            
    def close(self) -> None:
        """Close Google Pub/Sub publisher (no-op as client manages connections)"""
        pass


class GooglePubSubConsumer(Consumer):
    """Google Pub/Sub implementation of Consumer"""
    
    def __init__(self, topic: str, subscription: str, project_id: str, 
                 serializer: Optional[Serializer] = None):
        super().__init__(topic, serializer)
        self.project_id = project_id
        self.subscription = subscription
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(project_id, subscription)
        
    def consume(self, callback: Callable[[Any], None], timeout: Optional[float] = None) -> None:
        """
        Consume messages from Google Pub/Sub subscription
        
        Args:
            callback: Function to call with each message
            timeout: How long to wait for messages (None = wait forever)
        """
        def message_callback(message):
            try:
                data = self.serializer.deserialize(message.data)
                callback(data)
                message.ack()
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                message.nack()
        
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, 
            callback=message_callback,
            flow_control=pubsub_v1.types.FlowControl(max_messages=100)
        )
        
        try:
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
            streaming_pull_future.result()  # Block until the shutdown is complete
            
    def close(self) -> None:
        """Close Google Pub/Sub subscriber (no-op as client manages connections)"""
        pass


# Factory function for creating producers
def create_producer(broker_type: str, topic: str, serializer: Optional[Serializer] = None, 
                   **kwargs) -> Producer:
    """
    Factory function to create a producer based on broker type
    
    Args:
        broker_type: Either 'kafka' or 'pubsub'
        topic: Topic name to produce to
        serializer: Serializer instance to use
        **kwargs: Additional broker-specific configuration
        
    Returns:
        Producer instance
    """
    if broker_type.lower() == 'kafka':
        return KafkaProducer(topic, serializer=serializer, **kwargs)
    elif broker_type.lower() == 'pubsub':
        return GooglePubSubProducer(topic, serializer=serializer, **kwargs)
    else:
        raise ValueError(f"Unknown broker type: {broker_type}")


# Factory function for creating consumers
def create_consumer(broker_type: str, topic: str, serializer: Optional[Serializer] = None,
                   **kwargs) -> Consumer:
    """
    Factory function to create a consumer based on broker type
    
    Args:
        broker_type: Either 'kafka' or 'pubsub'
        topic: Topic name to consume from
        serializer: Serializer instance to use
        **kwargs: Additional broker-specific configuration
        
    Returns:
        Consumer instance
    """
    if broker_type.lower() == 'kafka':
        return KafkaConsumer(topic, serializer=serializer, **kwargs)
    elif broker_type.lower() == 'pubsub':
        return GooglePubSubConsumer(topic, serializer=serializer, **kwargs)
    else:
        raise ValueError(f"Unknown broker type: {broker_type}")
