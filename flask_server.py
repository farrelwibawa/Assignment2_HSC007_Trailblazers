import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)  # Perbaikan di sini

# Use environment variable for MongoDB URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://trailblazers:inuklimpung@trailblazers.pe08k.mongodb.net/?retryWrites=true&w=majority&appName=Trailblazers")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["sensor_data_db"]  
collection = db["sensor_readings"]

@app.route('/sensor_data', methods=['POST'])
def receive_data():
    try:
        data = request.json  
        required_fields = ["device_id", "temp", "humidity", "light", "motion"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        data["timestamp"] = datetime.utcnow()
        collection.insert_one(data)

        return jsonify({"message": "Sensor data saved successfully!", "data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':  # Perbaikan di sini
    app.run(host='0.0.0.0', port=5000, debug=True)
