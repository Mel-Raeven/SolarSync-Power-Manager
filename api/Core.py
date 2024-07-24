from flask import Flask, Response, request, jsonify
from api.Cred import *
import json
import os

app = Flask(__name__)
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
    # Get the list of plugs
    plugs: list[str] = ['Plug 1', 'Plug 2', 'Plug 3']  # Replace with your actual list of plugs

    # Return the list of plugs as a response
    return jsonify({'plugs': plugs})

@app.route(rule='/add_plugs', methods=['post'])
def add_plugs():
    # Get the plugs data from the request
    plugs_data = request.json
    print(plugs_data)
    # Check if the required fields are present in the request
    if 'name' not in plugs_data or 'type' not in plugs_data or 'config' not in plugs_data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Read the existing plugs from the JSON file
    with open(file='config/added-plugs.json') as file:
        existing_plugs = json.load(file)

    # Check if the plug with the same name or config already exists
    for plug in existing_plugs['plugs']:
        if plug['name'] == plugs_data['name']:
            return jsonify({'error': 'Plug with the same name already exists'}), 400
        if plug['config'] == plugs_data['config']:
            return jsonify({'error': 'Plug with the same config already exists'}), 400

    # Add the new plug to the existing plugs
    existing_plugs['plugs'].append(plugs_data)

    # Write the updated plugs to the JSON file
    with open(file='config/added-plugs.json', mode='w') as file:
        json.dump(existing_plugs, file)

    # Return a success response
    return jsonify({'message': 'Plugs added successfully'})


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
    app.run(ssl_context='adhoc')

if __name__ == '__main__':
    existence_check = check_config_files_exist(config_files)
    if existence_check is None:
        start_api()
    else:
        raise RuntimeError('Error creating config files')