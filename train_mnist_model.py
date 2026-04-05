import sys
import tensorflow as tf
from model_functions import train_and_save_model

# Load MNIST digit dataset for handwritten digit classification
mnist = tf.keras.datasets.mnist
(x_train, y_train), _ = mnist.load_data()

if __name__=='__main__':
    epochs = int(sys.argv[1])
    model_name = sys.argv[2]
    train_and_save_model(x_train, y_train, epochs, model_name)