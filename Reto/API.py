from flask import Flask, request, jsonify

app = Flask(__name__)

# Variable to store the last updated simulation data
simulation_data = {}

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
