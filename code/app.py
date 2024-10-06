from flask import Flask, render_template, request, redirect, url_for, jsonify, render_template_string
import uuid
import json
import time
import os
import requests

app = Flask(__name__)

DATA_FILE = 'data.json'
# OpenWeather API settings
OPENWEATHER_API_KEY = ''


# Function to load existing data from the JSON file
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# Function to save data to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        projectname = request.form['projectname']
        sitelocation = request.form['sitelocation']
        buildingtype = request.form['buildingtype']
        building_height = request.form['building_height']
        building_size = request.form['building_size']
        unique_id = str(uuid.uuid4())

        try:
            lat, lon = map(float, sitelocation.split(','))
        except ValueError:
            return jsonify({"error": "Invalid location format! Use 'latitude,longitude'."}), 400

        # Load existing data
        data_store = load_data()

        if not isinstance(data_store, dict):
            return jsonify({"error": "Data format error!!"}), 500

        data_store[unique_id] = {
            'unique_id': unique_id,
            'username': username,
            'projectname': projectname,
            'sitelocation': sitelocation,
            'lat': lat,
            'lon': lon,
            'buildingtype': buildingtype,
            'building_height': building_height,
            'building_size': building_size
        }

        save_data(data_store)

        time.sleep(1)

        api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"

        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()
            data_store[unique_id].update(api_response.json())
            save_data(data_store)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500
        return redirect(url_for('output', unique_id=unique_id))
    return render_template('index.html')


@app.route('/output/')
def output():
    unique_id = request.args.get('unique_id')
    data = load_data()
    data_temp = data[unique_id]

    if data_temp:
        return render_template('output.html', data_temp=data_temp)
    else:
        return "No data found for the provided ID", 404


@app.route('/history')
def display():
    data = load_data()
    data_all = []
    for d in data.values():
        data_hist = {
            "username": d.get('username', 'N/A'),
            "projectname": d.get('projectname', 'N/A'),
            "sitelocation": d.get('sitelocation', 'N/A'),
            "buildingtype": d.get('buildingtype', 'N/A'),
            "score": d.get('score', 'N/A'),
        }
        data_all.append(data_hist)
    return render_template('history.html', data_all=data_all)


if __name__ == '__main__':
    app.run(debug=True)