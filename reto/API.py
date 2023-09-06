
from flask import Flask, request, jsonify

# Guardar informacion de la simulacion
simulation_data = {}
num_robots = None  # Inicializar

app = Flask(__name__)

@app.route('/api/params', methods=['POST', 'GET'])
def set_params():
    global num_robots  # Declarada como global, no hace diferencia
    try:
        if request.method == 'POST': # Esta parte se llama desde unity
            # Recibir informacion del JSON, y convertir a diccionario
            data = request.json  # Parse JSON
            num_robots = int(data['num_robots']) # Sacar el valor

           

            return jsonify({"status": "Parameters set successfully!"}), 200
        
        elif request.method == 'GET':
            # Regresar el numero de robots, esta parte se llama desde python server
            return jsonify({"num_robots": num_robots}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error"}), 500


@app.route('/api/update', methods=['POST', 'GET'])
def update():
    global simulation_data  # Declarada como global
    
    try:
        if request.method == 'POST': # Esta parte se llama desde la simulacion de mesa de python
            # Parse jSON
            simulation_data = request.json
            
            # Imprimir informacion recibida
            print("Received Data:")
            print(simulation_data)
            
            return jsonify({"status": "success"}), 200

        elif request.method == 'GET': # Esta parte se llama desde unity
            # Return the last updated simulation data
            print("Sending Data:")
            print(simulation_data)
            return jsonify(simulation_data), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)