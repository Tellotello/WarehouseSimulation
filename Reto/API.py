
from flask import Flask, request, jsonify

# Variable to store the last updated simulation data and simulation parameters
simulation_data = {}
num_robots = None  # Variable to hold the number of robots

app = Flask(__name__)

@app.route('/api/params', methods=['POST', 'GET'])
def set_params():
    global num_robots  # Declare as global to modify
    try:
        if request.method == 'POST':
            # Parse the number of robots from the incoming POST request
            data = request.json  # Parse JSON data
            num_robots = int(data['num_robots'])

            # Here, set this parameter for your Mesa Model
            # ...

            return jsonify({"status": "Parameters set successfully!"}), 200
        
        elif request.method == 'GET':
            # Return the current number of robots
            return jsonify({"num_robots": num_robots}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error"}), 500


@app.route('/api/update', methods=['POST', 'GET'])
def update():
    global simulation_data  # Declare as global to modify
    
    try:
        if request.method == 'POST':
            # Parse JSON data from the incoming POST request
            simulation_data = request.json
            
            # Print the received data to the console
            print("Received Data:")
            print(simulation_data)
            
            return jsonify({"status": "success"}), 200

        elif request.method == 'GET':
            # Return the last updated simulation data
            print("Sending Data:")
            print(simulation_data)
            return jsonify(simulation_data), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
