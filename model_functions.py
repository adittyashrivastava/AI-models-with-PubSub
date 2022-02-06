import tensorflow as tf
import numpy as np

#Build basic architecture of the CNN model supposed to be trained
def build_model(number_of_categories:int, input_shape:tuple):
    #Build model functionally
    input = tf.keras.layers.Input(shape=input_shape, dtype='float16')
    x = tf.keras.layers.Conv2D(filters=8, kernel_size=(3, 3), padding='same', activation='relu')(input)
    x = tf.keras.layers.MaxPool2D(pool_size=(2, 2))(x)
    x = tf.keras.layers.Conv2D(filters=16, kernel_size=(3, 3), padding='same', activation='relu')(x)
    x = tf.keras.layers.MaxPool2D(pool_size=(2, 2))(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(units=64, activation='relu')(x)
    x = tf.keras.layers.Dense(units=32, activation='relu')(x)
    output = tf.keras.layers.Dense(units=number_of_categories, activation='softmax')(x)

    model = tf.keras.Model(inputs=input, outputs=output)

    #Compile the model with optimizer and loss function
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])
    return model

#Train the model on a foreign dataset
def train_and_save_model(x_train, y_train, epochs:int, model_name:str):
    #Get the number of classes in the training data
    number_of_categories = len(set(list(y_train)))

    #Get the input shape of a single training element
    X_train = tf.expand_dims(x_train, axis=-1)
    input_shape = X_train.shape[1:]

    #Build basic architecture of model
    model = build_model(number_of_categories, input_shape)

    #Get basic summary of model architecture
    model.summary()

    #Train the model on dataset
    model.fit(x_train, y_train, epochs=epochs)

    #Save model to given folder topic_path
    tf.keras.models.save_model(model=model, filepath=model_name)

    return

def get_model_prediction(x_test, model_path:str):

    model = tf.keras.models.load_model(model_path)
    if len(x_test.shape)==3:
        X_test = tf.expand_dims(x_test, axis=0)
    else:
        X_test = x_test

    Y = tf.math.argmax(model(X_test), axis=1)

    return list(np.array(Y))
