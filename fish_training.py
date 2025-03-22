import tensorflow as tf
from tensorflow.keras import layers, models # type: ignore
from tensorflow.keras.utils import image_dataset_from_directory # type: ignore
from sklearn.utils.class_weight import compute_class_weight # type: ignore
import numpy as np

# definisce la directory che fa da dataset
DATASET_DIR = "archive"

# data augmentation: flip orizzontale, rotazione, zoom e modifica al contrasto
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.2)
])

# carica dataset: immagini compresse a 224x224, batch di 32 immagini
train_dataset = image_dataset_from_directory(
    f"{DATASET_DIR}/train",
    image_size=(224, 224),
    batch_size=32,
    label_mode="int"
)

test_dataset = image_dataset_from_directory(
    f"{DATASET_DIR}/test",
    image_size=(224, 224),
    batch_size=32,
    label_mode="int"
)

# salva classi
class_names = train_dataset.class_names  # da fare sempre PRIMA di trasformare i dati
print(f"Classi trovate: {class_names}")

# bilancia il peso di ogni classe
class_weights = compute_class_weight(
    class_weight='balanced',  
    classes=np.unique(class_names), 
    y=class_names
)
class_weights = dict(enumerate(class_weights))

# normalizza gli input
AUTOTUNE = tf.data.AUTOTUNE
train_dataset = train_dataset.map(lambda x, y: (x / 255.0, y)).cache().prefetch(buffer_size=AUTOTUNE)
test_dataset = test_dataset.map(lambda x, y: (x / 255.0, y)).cache().prefetch(buffer_size=AUTOTUNE)
# in caso di data augmentation esterna al modello: train_dataset = train_dataset.map(lambda x, y: (data_augmentation(x, training=True), y))

# struttura del modello
num_classes = len(class_names)
model = models.Sequential([
    data_augmentation, # data augmentation interna al modello
    layers.Conv2D(64, (3, 3), activation="relu", input_shape=(224, 224, 1)),
    layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
    layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(256, (3, 3), activation="relu", padding="same"), 
    layers.Conv2D(256, (3, 3), activation="relu", padding="same"),
    layers.Conv2D(256, (3, 3), activation="relu", padding="same"),   
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(512, (3, 3), activation="relu", padding="same"), 
    layers.Conv2D(512, (3, 3), activation="relu", padding="same"),  
    layers.Conv2D(512, (3, 3), activation="relu", padding="same"), 
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(512, (2, 2), activation="relu", padding="same"), 
    layers.Conv2D(512, (2, 2), activation="relu", padding="same"), 
    layers.Conv2D(512, (3, 3), activation="relu", padding="same"), 
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(4096, activation="relu"),
    layers.Dense(4096, activation="relu"),
    layers.Dropout(0.5),  # Dropout to prevent overfitting
    layers.Dense(num_classes, activation="softmax")
])

# learning rate schedule: il learning rate diminuisce andando avanti con le epoche 
# (il learning rate dovrebbe essere diminuito con l'aumentare di neuroni o layer)
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=0.0001, decay_steps=1000, decay_rate=0.9
)
# compiling
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule), loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# funzione per l'early stopping che si attiva se la perdita in testing diminuisce per 5 epoche consecutive
early_stopping = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1)

# training per 100 epoche con eventuale early stopping e classi pesate
model.fit(train_dataset, epochs=200, validation_data=test_dataset, callbacks=[early_stopping], class_weight=class_weights)

# valuta perdita e accuratezza
loss, accuracy = model.evaluate(test_dataset)
print(f"Loss: {loss}")
print(f"Accuracy: {accuracy}")

# salva il modello con estensione .keras
model.save("fishcake15.keras")