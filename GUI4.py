from PIL import Image
from tensorflow.keras import models # type: ignore
import numpy as np
import webview as wv

# IMAGE CLASSIFICATION
# carica modello
model = models.load_model("fishcake21.keras")
#class_names = ["pesce pagliaccio", "corallo", "granchio", "delfino", "anguilla", "medusa", "pesce leone", "aragosta", "pesce palla", "anemone", "razza", "riccio di mare", "squalo", "stella marina"]
classNames = ["pesce pagliaccio", "granchio", "delfino", "anguilla", "medusa", "orca", "pesce scorpione", "aragosta", "nautilus", "nudibranco", "polpo", "lontra", "pinguino", "pesce palla", "anemone", "razza", "riccio di mare", "cavalluccio marino", "foca", "squalo", "gambero", "seppia", "stella marina", "tartaruga marina", "balena"]

class API:
    # funzione che classifica l'immagine e restituisce il risultato.
    def classifyImg(self, imgArr):
        finalArr = imgArr
        finalArr = np.expand_dims(finalArr, axis=0)
        predictions = model.predict(finalArr)
        global predictedClass
        predictedClass = classNames[np.argmax(predictions)]
        confidence = np.max(predictions) * 100
        if confidence >= 20:
            return f"{predictedClass} al {confidence:.2f}%"
        else:
            return "Animale non identificato"
        
api = API()

window = wv.create_window("SeaSentinel", "./src/index.html", fullscreen=True, js_api=api)
wv.start()