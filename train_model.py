import sys
import tensorflow as tf
from model_functions import train_and_save_model

fashion_mnist = tf.keras.datasets.fashion_mnist
(x_train, y_train), _ = fashion_mnist.load_data()

if __name__=='__main__':
    epochs = int(sys.argv[1])
    model_name = int(sys.argv[2])
    train_and_save_model(x_train, y_train, epochs, model_name)
