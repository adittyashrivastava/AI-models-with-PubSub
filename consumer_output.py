"""
Consumer script that receives model outputs and processes them
using the new class-based design
"""

import os
import numpy as np
import logging
import cv2
from datetime import datetime
from brokers import Broker
from serializers import NumpySerializer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_output(output_array: np.ndarray) -> None:
    """
    Process the model output
    
    Args:
        output_array: Model prediction output as numpy array
    """
    try:
        logging.info(f"Received output with shape: {output_array.shape}")
        
        # For demonstration, let's save the output as an image if it has the right shape
        # This assumes the output might be an image or can be visualized as one
        if len(output_array.shape) >= 2:
            # Normalize to 0-255 range if needed
            if output_array.max() <= 1.0:
                output_array = (output_array * 255).astype(np.uint8)
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f'./output/prediction_{timestamp}.png'
            
            # Create output directory if it doesn't exist
            os.makedirs('./output', exist_ok=True)
            
            # Save the output
            cv2.imwrite(output_path, output_array)
            logging.info(f"Output saved to {output_path}")
        else:
            # For 1D arrays, just log the values
            logging.info(f"Prediction values: {output_array}")
            
            # You could save to a CSV or database here
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f'./output/prediction_{timestamp}.npy'
            os.makedirs('./output', exist_ok=True)
            np.save(output_path, output_array)
            logging.info(f"Output saved to {output_path}")
            
    except Exception as e:
        logging.error(f"Error processing output: {e}")
        raise

def main():
    # Initialize broker
    broker = Broker()
    
    # Output topic
    output_topic = os.getenv('OUTPUT_TOPIC', 'output-topic')
    
    # Create consumer with NumpySerializer
    consumer = broker.get_consumer(output_topic, serializer=NumpySerializer())
    
    try:
        logging.info(f"Starting to consume from {output_topic} via {broker.broker_type}")
        
        # Start consuming messages
        if broker.is_kafka:
            # For Kafka, we can set max_messages for demo purposes
            consumer.consume(process_output, max_messages=10)
        else:
            # For Pub/Sub, we can set a timeout
            consumer.consume(process_output, timeout=300)  # 5 minutes
            
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"Error in consumer: {e}")
        raise
    finally:
        # Clean up
        consumer.close()
        logging.info("Consumer closed")

if __name__ == "__main__":
    main()
