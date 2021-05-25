import tensorflow as tf
from .settings import CHECKPOINT_PATH


def get_model(n):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(n, activation='relu'),
        tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.001, momentum=0.9), 
              loss=tf.keras.losses.mean_squared_error,
              metrics=tf.keras.metrics.MAE)
    model.load_weights(CHECKPOINT_PATH)
    return model
