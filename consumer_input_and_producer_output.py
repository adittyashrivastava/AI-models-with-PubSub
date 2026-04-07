"""
Consumer/Producer script that receives images, processes them with a model,
and sends the results using the new class-based design
"""

import os
import numpy as np
import logging
from model_functions import load_model, predict
from brokers import Broker
from serializers import NumpySerializer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_image(image_array: np.ndarray, model, producer) -> None:
    """
    Process an image with the model and send the result
    
    Args:
        image_array: Input image as numpy array
        model: Loaded model
        producer: Producer instance to send results
    """
    try:
        # Run prediction
        logging.info(f"Processing image with shape: {image_array.shape}")
        prediction = predict(model, image_array)
        
        # Send prediction result
        producer.send(prediction)
        logging.info(f"Prediction sent successfully. Shape: {prediction.shape}")
        
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        raise

def main():
    # Initialize broker
    broker = Broker()
    
    # Topics
    input_topic = os.getenv('INPUT_TOPIC', 'input-topic')
    output_topic = os.getenv('OUTPUT_TOPIC', 'output-topic')
    
    # Load the model
    model_path = './assets/imagenet_model.pkl'
    logging.info(f"Loading model from {model_path}")
    model = load_model(model_path)
    
    # Create consumer and producer with NumpySerializer
    consumer = broker.get_consumer(input_topic, serializer=NumpySerializer())
    producer = broker.get_producer(output_topic, serializer=NumpySerializer())
    
    try:
        logging.info(f"Starting to consume from {input_topic} via {broker.broker_type}")
        logging.info(f"Will produce to {output_topic}")
        
        # Define callback for processing messages
        def message_callback(image_array):
            process_image(image_array, model, producer)
        
        # Start consuming messages
        if broker.is_kafka:
            # For Kafka, we can set max_messages for demo purposes
            consumer.consume(message_callback, max_messages=10)
        else:
            # For Pub/Sub, we can set a timeout
            consumer.consume(message_callback, timeout=300)  # 5 minutes
            
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"Error in consumer: {e}")
        raise
    finally:
        # Clean up
        consumer.close()
        producer.close()
        logging.info("Consumer and producer closed")

if __name__ == "__main__":
    main()
