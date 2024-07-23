from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to select device type
@app.route('/select_device_type', methods=['POST'])
def select_device_type():
    # Get the selected device type from the request
    device_type= request.json.get('device_type')

    # Perform any necessary operations based on the selected device type
    # ...

    # Return a response
    return jsonify({'message': 'Device type selected successfully'})

# Endpoint to return list of plugs
@app.route('/list_plugs', methods=['GET'])
def list_plugs():
    # Get the list of plugs
    plugs: list[str] = ['Plug 1', 'Plug 2', 'Plug 3']  # Replace with your actual list of plugs

    # Return the list of plugs as a response
    return jsonify({'plugs': plugs})

# Endpoint to scan for devices
@app.route('/scan_devices', methods=['GET'])
def scan_devices():
    # Perform the device scanning operation
    # ...

    # Return a response
    return jsonify({'message': 'Device scanning completed'})

def start_api() -> None:
    app.run()

if __name__ == '__main__':
    start_api()