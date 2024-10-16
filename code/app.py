from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
import json
import time
import os
import requests
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)
DATA_FILE = 'data.json'

unique_id = ""
# OpenWeather API settings
OPENWEATHER_API_KEY = '<api-key>'

# Watsonx.ai API settings
WATSONX_URL = "<url>"
WATSONX_MODEL_ID = "meta-llama/llama-3-8b-instruct"
WATSONX_MODEL_ID2 = "ibm/granite-13b-chat-v2"
WATSONX_PROJECT_ID = "<id>"
WATSONX_AUTH_TOKEN = "<token>"

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


def extract_json_from_markdown(response_text):
    # Look for the JSON block between ```json and ```
    json_block = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if not json_block:
            json_block = re.search(r"```\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if json_block:
        json_str = json_block.group(1)  # Extract the JSON part
        # Step 1: Replace number ranges (e.g., 25-35) with quoted strings ("25-35")
        json_str = re.sub(r'(\d+)\s*-\s*(\d+)', r'"\1-\2"', json_str)
        # Step 2: Identify numeric values followed by non-standard units (e.g., mm/year, dB) and quote them
        json_str = re.sub(r'(\d+)\s*([a-zA-Z/%]+)', r'"\1 \2"', json_str)
        try:
            return json_str
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {e}")
    else:
        raise ValueError("No JSON found between ```json and ``` markers.")


def extract_add_score(text):
    print(text)
    # match = re.search(r'Average Score:\s*([\d.]+)/10', text)
    match = re.search(r'Average score:\s*(\d+\.\d+)/10', text)
    print("Match is ")
    print(match)
    if match:
        return float(match.group(1))
    return None


# Function to get information from Watsonx.ai
def get_watsonx_info(buildingtype, lat, lon, name):
    prompt = f"""We are constructing a building of type {buildingtype} at location having latitude={lat}, longitude={lon} which is in city {name}. Please give us information about the area and below points:
    1.zoning laws
    2.soil type in aspect of bearing capacity, moisture content, plasticity index, compaction characteristics, shear strength, permeability, consolidation properties, PH level.
    3.Site Topography
    4.environmental conditions
    5.essentials water in aspect of water source in that area and ground water level
    6.utility access in aspect of electricity, network, water, transportation
    7.terrain history in aspect of whether that land is prone to natural calamities
    8.Safety Standards
    9.Pollution/Noise considerations in this area
    Please respond exact details in measurement or numbers in very short and exact with only in **valid JSON** in ```json ``` format only, no any other text"""
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1.05
        },
        "model_id": WATSONX_MODEL_ID,
        "project_id": WATSONX_PROJECT_ID
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WATSONX_AUTH_TOKEN}"
    }
    response = requests.post(WATSONX_URL, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    data = response.json()
    generated_text=data['results'][0]['generated_text']
    return generated_text


# Function to get final O/P using granite model
def get_query_watsonx(unique_id):
    data_json = load_data()
    if unique_id not in data_json:
        return jsonify({"error": "No record found for this unique_id"}), 404
    data=data_json[unique_id]
    prompt = f"""Given the data below, create a detailed descriptive report that evaluates the location for the construction of the building. 
    Please assess the following parameters and score for each: 
    Weather conditions
    Zoning laws
    Soil characteristics
    Site topography
    Environmental conditions
    Water resources
    Utility access
    Terrain history
    Safety standards
    Pollution and noise levels
    For each parameter, provide:
    1.A descriptive evaluation based on the provided data, highlighting both positive aspects and potential risks. 
    2.A score from 1 to 10 for each parameter based on its suitability for the construction. 
    3.At the end of the report, calculate and provide an average score based on all the parameters. Structure the report in a well-organized and professional manner.
    {data}"""

    # Give us exact details in measurement or numbers in short JSON format only. Provide direct json file, don't add any other lines at start or end of JSON"""
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1.05
        },
        "model_id": WATSONX_MODEL_ID2,
        "project_id": WATSONX_PROJECT_ID
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WATSONX_AUTH_TOKEN}"
    }
    response = requests.post(WATSONX_URL, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    data = response.json()
    generated_text = data['results'][0]['generated_text']
    report_data(generated_text)
    return generated_text


def report_data(report):

    # Preprocess the input to remove excess newlines and standardize formatting
    report = report.strip().replace("\n\n", "\n")
    report = report.strip().replace("**", "")

    # Regular expression to capture parameter names and scores
    pattern = r"^(?P<Parameter>.+?)\n.*?Score:\s*(?P<Score>\d+)/10"

    # Extracting parameters and scores using the updated pattern
    matches = re.findall(pattern, report, re.MULTILINE | re.DOTALL)

    # Check if any matches are found
    if matches:
        # Create DataFrame from matches
        df = pd.DataFrame(matches, columns=['Parameter', 'Score'])

        # Convert Score column to integer
        df['Score'] = df['Score'].astype(int)

        # Clean the Parameter column to remove any trailing spaces
        df['Parameter'] = df['Parameter'].str.strip()

        # Display the table without the index
        print("\nExtracted Parameters and Scores:\n")
        # Optionally, save to a CSV if needed
        df.to_csv('location_evaluation_scores.csv', index=False)
        createGraph('location_evaluation_scores.csv')
        print(df.to_string(index=False))
        return df.to_string(index=False)
    else:
        print("No parameters and scores found. Please check the format of your input.")

def createGraph(file_path):
    global unique_id
    # CSV file path (adjust as necessary)
    csv_file_path = file_path
    # Read the dataset from CSV
    factors, scores = read_data_from_csv(csv_file_path)
    # Create the bar plot
    bars = plt.bar(factors, scores, color='maroon', width=0.4)
    # Fixing overlapping labels by rotating them
    plt.xticks(rotation=45, ha="right")
    # Display values on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom')
    # Set y-axis ticks to reflect a scale of 10
    plt.yticks(np.arange(0, 11, 1))
    plt.xlabel("Factors")
    plt.ylabel("Score (Out of 10)")
    plt.title("Evaluation Report (Scale of 10)")
    # Adjust layout to prevent cutoff
    plt.tight_layout()
    # Define the specific path to save the image
    output_directory = 'static/images'
    os.makedirs(output_directory, exist_ok=True)  # Create directory if it doesn't exist
    # Save the figure to the specific path
    file_path = os.path.join(output_directory, f"bar_graph_{unique_id}.png")
    plt.savefig(file_path, format='png')

# Function to read data from CSV
def read_data_from_csv(file_path):
    # Read CSV into a pandas DataFrame
    df = pd.read_csv(file_path)
    # Extract 'Factors' and 'Score' columns and convert to lists
    factors = df['Parameter'].tolist()
    scores = df['Score'].tolist()
    return factors, scores

@app.route('/', methods=['GET', 'POST'])
def index():
    global unique_id

    if request.method == 'POST':
        username = request.form['username']
        projectname = request.form['projectname']
        sitelocation = request.form['sitelocation']
        buildingtype = request.form['buildingtype']
        building_height = request.form['building_height']
        building_size = request.form['building_size']
        unique_id = str(uuid.uuid4())
        unique_id = unique_id
        name = ''
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
        
        time.sleep(18)
        # OpenWeather API call
        api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()

            #extracting city name from api_response
            weather_data = api_response.json()
            name = weather_data.get('name','')

            #update the data store with weather data and city name
            data_store[unique_id].update(weather_data)
            data_store[unique_id]['city_name']= name #adding city name to data
            save_data(data_store)
            
            # Watsonx.ai API call
            try:
                    data_store = load_data()  # Load the existing data
                    if unique_id not in data_store:
                        return jsonify({"error": "No record found for this unique_id"}), 404
                    
                    watsonx_info_from_model = get_watsonx_info(buildingtype, lat, lon, name)
                    watsonx_info = extract_json_from_markdown(watsonx_info_from_model)
                    # Update the existing entry with Watsonx info
                    data_store[unique_id].update({"watsonx_info": watsonx_info})
                    # Save the updated data back to the file
                    save_data(data_store)
                    query_watsonx = get_query_watsonx(unique_id)
                    
                    # Extract Average Score from output
                    data_store = load_data()
                    avg_score = extract_add_score(query_watsonx)
                    print(avg_score)
                    data_store[unique_id].update({"score": avg_score})
                    save_data(data_store)
            except Exception as e:
                    return jsonify({"error": str(e)}), 500
        except requests.exceptions.RequestException as e:
                return jsonify({"error": str(e)}), 500
        return redirect(url_for('output', query_watsonx=query_watsonx))
    return render_template('index.html')


@app.route('/output/')
def output():
    global unique_id
    file_path = os.path.join('static/images', f"bar_graph_{unique_id}.png")
    image_path = f"bar_graph_{unique_id}.png"
    data_temp = request.args.get('query_watsonx')
    if data_temp:
        return render_template('output.html', data_temp=data_temp, image_path=image_path)
    else:
        return "No data found for the provided ID", 404


@app.route('/history')
def display():
    data = load_data()
    data_all = []
    for d in data.values():
        data_hist = {
            "unique_id": d.get('unique_id', 'N/A'),
            "username": d.get('username', 'N/A'),
            "projectname": d.get('projectname', 'N/A'),
            "sitelocation": d.get('sitelocation', 'N/A'),
            "buildingtype": d.get('buildingtype', 'N/A'),
            "score": d.get('score', 'N/A'),
        }
        data_all.append(data_hist)
    return render_template('history.html', data_all=data_all)


@app.route('/compare/<unique_id>')
def compare(unique_id):
    print(unique_id)
    return render_template('compare.html', unique_id=unique_id)


if __name__ == '__main__':
    app.run(debug=True)
