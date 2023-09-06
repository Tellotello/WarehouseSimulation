from model_bien import Estante
from model_bien import BandaEntrada
from model_bien import BandaSalida
from model_bien import EstacionDeCarga
from model_bien import RobotDeCarga
from model_bien import Paquete
from model_bien import Almacen
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



chart_paquetes = mesa.visualization.ChartModule(
    [{"Label": "Paquetes_almacenados", "Color": '#36A2EB', "label": "Paquetes almacenados"}],
    50, 200,
    data_collector_name="datacollector"
)
chart_paquetes_entregados = mesa.visualization.ChartModule(
    [{"Label": "Paquetes_entregados", "Color": '#36A2EB', "label": "Paquetes entregados"}],
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
    
    Almacen, [grid, chart_paquetes, chart_paquetes_entregados],
    "botCleaner", model_params, 8521
)
   
    server.launch(open_browser=True)

num_robots = None
while num_robots is None: # Esperar a que llegue el numero de robots, se cicla hasta conseguirlo
    print("Waiting for the number of robots to be set...")
    
    try:
        # Intentar hacer una get request al api
        response = requests.get('http://127.0.0.1:5000/api/params')
        if response.status_code == 200:
            data = response.json()
            num_robots = data.get("num_robots", None)
            
            if num_robots is not None:
                print(f"Number of robots set to {num_robots}")
                break  # Salir cuando ya se encontró
            
    except Exception as e:
        print(f"An error occurred: {e}")

    time.sleep(1)  # Esperar

# Correr el servidor
run_mesa_server(num_robots)

