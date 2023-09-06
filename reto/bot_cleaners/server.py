import mesa

from .model import Almacen, Estante, BandaEntrada, BandaSalida, EstacionDeCarga, RobotDeCarga, Paquete


MAX_NUMBER_ROBOTS = 20

## reto

def agent_portrayal(agent):
    if isinstance(agent, Estante):
        portrayal = {"Shape": "rect", "Filled": "true", "Color": "orange", "Layer": 1, "w": 0.9, "h": 0.9, "text_color": "black"}
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
        portrayal = {"Shape": "circle", "Filled": "true", "Color": "green", "Layer": 1, "r": 0.9, "text_color": "white"}
        # portrayal["Color"] = "#ccbeaf"
        portrayal["text"] = f"{round(agent.carga)}"
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
# text_visualization = mesa.visualization.TextVisualization(Almacen

# )

server = mesa.visualization.ModularServer(
    Almacen, [grid, chart_paquetes, chart_paquetes_entregados],
    "Almacén automatizado",
    model_params, 8521
)
