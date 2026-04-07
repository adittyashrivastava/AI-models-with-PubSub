"""
Updated Broker class that uses the new Producer and Consumer classes
"""

import os
from typing import Optional
from messaging import Producer, Consumer, create_producer, create_consumer
from serializers import Serializer


class Broker:
    """
    Main broker class that provides producer and consumer instances
    based on the configured broker type (Kafka or Google Pub/Sub)
    """
    
    def __init__(self, broker_type: Optional[str] = None):
        """
        Initialize broker with specified type
        
        Args:
            broker_type: 'kafka' or 'pubsub' (defaults to environment variable BROKER_TYPE)
        """
        self.broker_type = broker_type or os.getenv('BROKER_TYPE', 'kafka').lower()
        if self.broker_type not in ['kafka', 'pubsub']:
            raise ValueError(f"Invalid broker type: {self.broker_type}. Must be 'kafka' or 'pubsub'")
            
    def get_producer(self, topic: str, serializer: Optional[Serializer] = None, 
                     **kwargs) -> Producer:
        """
        Get a producer instance for the specified topic
        
        Args:
            topic: Topic name to produce to
            serializer: Serializer instance to use
            **kwargs: Additional broker-specific configuration
            
        Returns:
            Producer instance
        """
        if self.broker_type == 'kafka':
            # Get Kafka-specific config from environment or kwargs
            bootstrap_servers = kwargs.pop('bootstrap_servers', 
                                         os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'))
            return create_producer('kafka', topic, serializer=serializer, 
                                 bootstrap_servers=bootstrap_servers, **kwargs)
        else:  # pubsub
            # Get Pub/Sub-specific config from environment or kwargs
            project_id = kwargs.pop('project_id', 
                                  os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'))
            return create_producer('pubsub', topic, serializer=serializer, 
                                 project_id=project_id, **kwargs)
    
    def get_consumer(self, topic: str, serializer: Optional[Serializer] = None,
                     **kwargs) -> Consumer:
        """
        Get a consumer instance for the specified topic
        
        Args:
            topic: Topic name to consume from
            serializer: Serializer instance to use
            **kwargs: Additional broker-specific configuration
            
        Returns:
            Consumer instance
        """
        if self.broker_type == 'kafka':
            # Get Kafka-specific config from environment or kwargs
            bootstrap_servers = kwargs.pop('bootstrap_servers', 
                                         os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'))
            group_id = kwargs.pop('group_id', 
                                os.getenv('KAFKA_GROUP_ID', 'default-group'))
            return create_consumer('kafka', topic, serializer=serializer, 
                                 bootstrap_servers=bootstrap_servers, 
                                 group_id=group_id, **kwargs)
        else:  # pubsub
            # Get Pub/Sub-specific config from environment or kwargs
            project_id = kwargs.pop('project_id', 
                                  os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'))
            subscription = kwargs.pop('subscription', 
                                    os.getenv('PUBSUB_SUBSCRIPTION', f'{topic}-subscription'))
            return create_consumer('pubsub', topic, serializer=serializer, 
                                 project_id=project_id, 
                                 subscription=subscription, **kwargs)
    
    @property
    def is_kafka(self) -> bool:
        """Check if broker is Kafka"""
        return self.broker_type == 'kafka'
    
    @property
    def is_pubsub(self) -> bool:
        """Check if broker is Google Pub/Sub"""
        return self.broker_type == 'pubsub'
