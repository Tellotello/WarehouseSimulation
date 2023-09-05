from model_bien import Estante, BandaEntrada, BandaSalida, EstacionDeCarga, RobotDeCarga, Paquete
from model_bien import Habitacion
import mesa.visualization
import time
import requests


MAX_NUMBER_ROBOTS = 20
M = N = 15

def agent_portrayal(agent):
    if isinstance(agent, Estante):
        portrayal = {"Shape": "rect", "Filled": "true", "Color": "orange", "Layer": 1, "w": 0.9, "h": 0.9}
        if agent.lleno:
            portrayal["Color"] = "red"
            portrayal["text"] = "Full"
        else:
            portrayal["Color"] = "orange"
            portrayal["text"] = ""
        return portrayal
    elif isinstance(agent, BandaEntrada):
        return{"Shape": "rect", "Filled": "true", "Color": "black", "Layer": 0, "w": 0.9, "h": 0.9}
    elif isinstance(agent, BandaSalida):
        return{"Shape": "rect", "Filled": "true", "Color": "black", "Layer": 0, "w": 0.9, "h": 0.9}
    elif isinstance(agent, EstacionDeCarga):
        return{"Shape": "rect", "Filled": "true", "Color": "gray", "Layer": 0, "w": 0.9, "h": 0.9}
    elif isinstance(agent, RobotDeCarga):
        portrayal = {"Shape": "circle", "Filled": "true", "Color": "green", "Layer": 1, "r": 0.9}
        # portrayal["Color"] = "#ccbeaf"
        portrayal["text"] = "H"
        return portrayal
    elif isinstance(agent, Paquete):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 2, "w": 0.7, "h": 0.7}
        portrayal["Color"] = "#ccbeaf"
        portrayal["text"] = "📦"
        return portrayal
        
grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 15, 15, 300, 300)

chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "Celdas", "Color": '#36A2EB', "label": "Celdas"}],
    50, 200,
    data_collector_name="datacollector"
)

model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        4,
        2,
        MAX_NUMBER_ROBOTS,
        1,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Seleciona la forma se posicionan los robots"
    ),
    "M": 15,
    "N": 15,
}

# Initialize the Mesa server
def run_mesa_server(num_robots):

    if num_robots is None:
        num_robots = 2  # Default value

    model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        num_robots,
        2,
        MAX_NUMBER_ROBOTS,
        1,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Seleciona la forma se posicionan los robots"
    ),
    "M": 15,
    "N": 15,
}
    server = mesa.visualization.ModularServer(
    Habitacion, [grid, chart_celdas],
    "botCleaner", model_params, 8521
)
   
    server.launch(open_browser=True)

num_robots = None
while num_robots is None:
    print("Waiting for the number of robots to be set...")
    
    try:
        # Make a GET request to the API
        response = requests.get('http://127.0.0.1:5000/api/params')
        if response.status_code == 200:
            data = response.json()
            num_robots = data.get("num_robots", None)
            
            if num_robots is not None:
                print(f"Number of robots set to {num_robots}")
                break  # Exit the loop
            
    except Exception as e:
        print(f"An error occurred: {e}")

    time.sleep(1)  # Wait for 1 second

run_mesa_server(num_robots)

# AAAAAAAAAAAA