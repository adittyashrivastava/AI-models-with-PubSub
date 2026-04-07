"""
Producer script that sends images to the message broker using the new class-based design
"""

import os
import cv2
import numpy as np
from brokers import Broker
from serializers import NumpySerializer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Initialize broker and get producer with NumpySerializer
    broker = Broker()
    input_topic = os.getenv('INPUT_TOPIC', 'input-topic')
    producer = broker.get_producer(input_topic, serializer=NumpySerializer())
    
    # Read and process images
    image_path = './assets/image.png'
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            logging.error(f"Failed to load image from {image_path}")
            return
            
        # Convert to RGB (OpenCV loads as BGR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Send image to broker
        logging.info(f"Sending image to {input_topic} via {broker.broker_type}")
        producer.send(image_rgb)
        logging.info("Image sent successfully")
        
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        raise
    finally:
        # Clean up
        producer.close()
        logging.info("Producer closed")

if __name__ == "__main__":
    main()
