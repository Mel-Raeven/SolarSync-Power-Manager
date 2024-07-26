from flask import Flask, Response, request, jsonify

from flask_cors import CORS, cross_origin
from api.Cred import *
from logic.KaKuConnector import KaKuHubConnector, KaKuPlugs
from logic.Plugs import ListPlugs
import json
import os

app = Flask(__name__)
CORS(app)
config_files = ['config/added-plugs.json', 'config/supported-devices.json']

def check_config_files_exist(file_paths):
    for file_path in file_paths:
        if not os.path.exists(f'configs/{file_path}'):
            with open(f'configs/{file_path}', 'w') as file:
                file.write('{}')
    return None

# Endpoint to return list of plugs
@app.route(rule='/list_plugs', methods=['GET'])
def list_plugs():
    # Read the list of plugs from the JSON file
    with open(file='config/found-plugs.json') as file:
        plugs = json.load(file)

    # Check if the file is empty
    if not plugs:
        # If the file is empty, run refresh_plugs()
        return refresh_plugs()

    # Return the list of plugs as a response
    return jsonify(plugs)

@app.route(rule='/refresh_plugs', methods=['GET'])
def refresh_plugs():
    # Get the list of plugs
    plugs = ListPlugs()  # Replace with your actual list of plugs
    print (plugs)
    # Return the list of plugs as a response
    return jsonify({"plugs": plugs})

@app.route(rule='/add_plugs', methods=['POST'])
def add_plugs():
    # Get the plugs data from the request
    plugs_data = request.json
    print(plugs_data)
    # Check if the required fields are present in the request
    if 'name' not in plugs_data or 'type' not in plugs_data or 'id' not in plugs_data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Read the existing plugs from the JSON file
    with open(file='config/added-plugs.json') as file:
        existing_plugs = json.load(file)

    # Check if the plug with the same name or config already exists
    for plug in existing_plugs['plugs']:
        if plug['name'] == plugs_data['name']:
            return jsonify({'error': 'Plug with the same name already exists'}), 400
        if 'id' in plug and plug['id'] == plugs_data['id']:
            return jsonify({'error': 'Plug with the same config already exists'}), 400

    # Add the new plug to the existing plugs
    existing_plugs['plugs'].append(plugs_data)

    # Write the updated plugs to the JSON file
    with open(file='config/added-plugs.json', mode='w') as file:
        json.dump(existing_plugs, file)

    # Return a success response
    return jsonify({'message': 'Plugs added successfully'})
    
@app.route(rule='/remove_plug', methods=['DELETE'])
def remove_plug():
    # Get the plug data from the request
    plug_data = request.json

    # Check if the required fields are present in the request
    if 'name' not in plug_data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Read the existing plugs from the JSON file
    with open(file='config/added-plugs.json') as file:
        existing_plugs = json.load(file)

    # Find the plug with the specified name
    for plug in existing_plugs['plugs']:
        if plug['name'] == plug_data['name']:
            # Remove the plug from the existing plugs
            existing_plugs['plugs'].remove(plug)

            # Write the updated plugs to the JSON file
            with open(file='config/added-plugs.json', mode='w') as file:
                json.dump(existing_plugs, file)

            # Return a success response
            return jsonify({'message': 'Plug removed successfully'})

    # If the plug is not found, return an error response
    return jsonify({'error': 'Plug not found'}), 404

@app.route(rule='/update_priority', methods=['PUT'])
def update_priority():
    # Get the plug data from the request
    plug_data = request.json

    # Check if the required fields are present in the request
    if 'name' not in plug_data or 'priority' not in plug_data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Read the existing plugs from the JSON file
    with open(file='config/added-plugs.json') as file:
        existing_plugs = json.load(file)

    # Find the plug with the specified name
    for plug in existing_plugs['plugs']:
        if plug['name'] == plug_data['name']:
            # Update the priority of the plug
            plug['priority'] = plug_data['priority']

            # Write the updated plugs to the JSON file
            with open(file='config/added-plugs.json', mode='w') as file:
                json.dump(existing_plugs, file)

            # Return a success response
            return jsonify({'message': 'Plug priority updated successfully'})

    # If the plug is not found, return an error response
    return jsonify({'error': 'Plug not found'}), 404

@app.route(rule='/add_device', methods=['POST'])
def authenticate():
    # Write the credentials to environment variables
    if request.json is None:
        return jsonify({'error': 'Credentials not provided'}), 400

    # Write the credentials to environment variables
    result = write_to_env(variables=request.json)
    if result == 'Device already added':
        return jsonify({'warning': result})
    else:
        return jsonify({'message': 'Authentication successful'})

@app.route(rule='/list_available_devices', methods=['GET'])
def list_available_devices() -> Response:
    # Read the supported devices from the JSON file
    with open(file='config/supported-devices.json') as file:
        supported_devices = json.load(file)

    # Return the list of supported devices as a response
    return jsonify(supported_devices)

def start_api() -> None:
    #app.run(ssl_context='adhoc')
    app.run()
    
if __name__ == '__main__':
    existence_check = check_config_files_exist(config_files)
    if existence_check is None:
        start_api()
    else:
        raise RuntimeError('Error creating config files')