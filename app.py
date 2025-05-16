from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import sqlite3
from keras.models import load_model
from keras.optimizers import Adam
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import pandas as pd

app = Flask(__name__)

# Load model
model = load_model('emotion_detection_model.h5', compile=False)
model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Initialize DB
def init_db():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emotion TEXT,
            rating INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def emotion_to_star(emotion):
    return {'Happy': 5, 'Neutral': 3, 'Sad': 2, 'Angry': 1}.get(emotion, 3)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        image_data = request.form['image']
        image_data = image_data.split(',')[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = image.convert('L')  # grayscale
        image = image.resize((64, 64))
        img_array = np.array(image).astype('float32') / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        img_array = np.expand_dims(img_array, axis=-1)

        prediction = model.predict(img_array)[0]
        emotion = emotion_labels[np.argmax(prediction)]
        rating = emotion_to_star(emotion)

        # Save to DB
        conn = sqlite3.connect("feedback.db")
        c = conn.cursor()
        c.execute("INSERT INTO feedback (emotion, rating, timestamp) VALUES (?, ?, ?)",
                  (emotion, rating, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        return jsonify({'emotion': emotion, 'rating': rating})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
