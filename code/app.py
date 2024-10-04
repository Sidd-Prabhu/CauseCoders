from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
import json
import time
import os

app = Flask(__name__)

data_store = {}
DATA_FILE = 'data.json'

# Initialize JSON file
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)


@app.route('/', methods=['GET', 'POST'])
def index():
    # output = ''
    if request.method == 'POST':
        username = request.form['username']
        projectname = request.form['projectname']
        sitelocation = request.form['sitelocation']
        buildingtype = request.form['buildingtype']
        building_height = request.form['building_height']
        building_size = request.form['building_size']
        unique_id = str(uuid.uuid4())

        data_store[unique_id] = {
            'username': username,
            'projectname': projectname,
            'sitelocation': sitelocation,
            'buildingtype': buildingtype,
            'building_height': building_height,
            'building_size': building_size
        }
        # Load existing data
        with open(DATA_FILE, 'r') as f:
            data_temp = json.load(f)

        # Add new entry to data
        data_temp.append(data_store.get(unique_id))

        # Write data back to JSON file
        with open(DATA_FILE, 'w') as f:
            json.dump(data_temp, f, indent=4)

        time.sleep(10)
        return redirect(url_for('output', unique_id=unique_id))
    return render_template('index.html')


@app.route('/output/')
def output():
    unique_id = request.args.get('unique_id')
    data = data_store.get(unique_id)

    if data:
        return render_template('output.html', username=data['username'], projectname=data['projectname'], sitelocation=data['sitelocation'], buildingtype=data['buildingtype'])
    else:
        return "No data found for the provided ID", 404


@app.route('/history')
def display():
    with open(DATA_FILE, 'r') as f:
        data_hist = json.load(f)
    return render_template('history.html', data_hist=data_hist)


if __name__ == '__main__':
    app.run(debug=True)
