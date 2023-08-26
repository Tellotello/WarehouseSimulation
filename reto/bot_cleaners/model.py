from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import matplotlib.pyplot as plt
import matplotlib as mlp

import numpy as np
import math
import time
import datetime



"""
CLASES RETO START Algo
"""

def distancia_entre_puntos(p1, p2):
    if p1 and p2:
        term_x = (p2[0] - p1[0])**2
        term_y = (p2[1] - p1[1])**2
        distance = math.sqrt(term_x + term_y)
        return round(distance, 3)
    else:
        return 1000

def get_agentes_pos(model, pos):
    agentes = model.grid.get_cell_list_contents([pos])
    return agentes

    
M = N = 15

class Estante(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # self.tipo = tipo
    
class BandaSalida(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    
    # def hay_paquete(self):
    #     agentes_banda = get_agentes_pos(self.model, self.pos)
    #     hay_paquete = False
    #     for i in agentes_banda:
    #         if isinstance(i, Paquete):
    #             hay_paquete = True
    #             break
    #     return hay_paquete

    
    # def contratar_robot_recoger(self):
    #     for i in RobotDeCarga.posiciones:
    #         distancias_robots = [(i[1], distancia_entre_puntos(self.pos, i[1]))]
        
    #     indice_min_distancia = min(distancias_robots, key=lambda x: x[1])[0]
    #     robot_cercano = get_agentes_pos(self.model, distancias_robots[indice_min_distancia][0])
    #     robot_cercano.recorrido.append(self.pos)

class BandaEntrada(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.paquetes = []
    

    def hay_paquete(self):
        for i in self.paquetes:
            if i[1] == -1:
                return True
        return False
        
    def registrar_paquetes(self):
        agentes_banda = get_agentes_pos(self.model, self.pos)
        for i in agentes_banda:
                if isinstance(i, Paquete) and self.paquete_registrado(i.unique_id) != True:
                    # print("Se registro un paquete")
                    self.paquetes.append([i.unique_id, -1])
                    
    
    def paquete_registrado(self, id):
        for i in self.paquetes:
            if i[0] == id:
                return True
        return False

    
    def contratar_robot_recoger(self):
        distancias_robots = []
        for i in Habitacion.robots:
            if self.contratado(i.unique_id) != True:
                distancias_robots.append((i.pos, distancia_entre_puntos(self.pos, i.pos)))
        
        # print(distancias_robots)
        pos_min_distancia = min(distancias_robots, key=lambda x: x[1])[0]
        robot_cercano = get_agentes_pos(self.model, pos_min_distancia)[0]
        # print(f'Se contrato al robot {robot_cercano.unique_id} que se encuentra a una distancia de {pos_min_distancia} contra las distancias {distancias_robots}')
        self.paquetes[0][1] = robot_cercano.unique_id # robot contratado
        robot_cercano.recorrido.append(self.pos)
    
    def paquete_recogido(self, paquete_id):
        for i in self.paquetes:
            if i[0] == paquete_id:
                id_registro_paquete = self.paquetes.index(i)
                self.paquetes.pop(id_registro_paquete)
    def contratado(self, robot_id):
        for i in self.paquetes:
            if i[1] == robot_id:
                return True
        return False



    def step(self):
        # print(f'Paquetes: {self.paquetes}')
        self.registrar_paquetes()
        # print("Se checa si hay paquete")
        if self.hay_paquete():
            self.contratar_robot_recoger()

    def advance(self):
        pass
        
class EstacionDeCarga(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = False



class Paquete(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None

class Pedido():
    def __init__(self, tipo):
        self.tipo = tipo

class RobotDeCarga(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.recorrido = []
        # RobotDeCarga.posiciones.append((self.unique_id, self.pos))

    def dirigirse(self, pos_final, lista_de_vecinos):
        if pos_final:
            distancias_vecinos = []
            vecinos_test = []
            # print(f'longitud lista de vecinos: {len(lista_de_vecinos)}')
            for i in range(len(lista_de_vecinos)):

                # Que no sea mueble ni este en celdas limpias
                # agente_vecino = get_agentes_pos(self.model, lista_de_vecinos[i].pos)[0]
                # agente_vecino = lista_de_vecinos[i]
                agente_vecino = get_agentes_pos(self.model, lista_de_vecinos[i])

                # print(f'checamos si vecino en pos {agente_vecino.pos} pasa condicion')
                if isinstance(agente_vecino, Estante) != True and isinstance(agente_vecino, BandaEntrada) != True and isinstance(agente_vecino, BandaSalida) != True:
                    # print("paso condicion")
                    # distancia = round(distancia_entre_puntos(agente_vecino.pos, pos_final), 3)
                    distancia = round(distancia_entre_puntos(lista_de_vecinos[i], pos_final), 3)
                    distancias_vecinos.append((i, distancia))
                    # vecinos_test.append((agente_vecino.pos, distancia))
                    vecinos_test.append((lista_de_vecinos[i], distancia))
                # else:
                    # print(f'vecino en pos {agente_vecino.pos} no paso la posicion')

            # print(f"vecinos_test: {vecinos_test}")
            if len(distancias_vecinos) > 0:
                index_min_distancia = min(distancias_vecinos, key=lambda x: x[1])[0]
                min_distancia = lista_de_vecinos[index_min_distancia]
                self.sig_pos = min_distancia
            else:
                self.sig_pos = self.pos
        else:
            self.sig_pos = self.pos
        # print(f'El robot {self.unique_id} se dirige a pos_final {pos_final} mediante {self.sig_pos} con las distancias de vecinos  {distancias_vecinos}')


    def step(self):

        lista_de_vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        lista_de_vecinos = self.model.grid.get_neighborhood(
            self.pos, 
            moore=False,
            include_center=False)
        
        for i in lista_de_vecinos:
            agente = get_agentes_pos(self.model, i)
            if len(agente) > 0:
                agente = agente[0]
                if isinstance(agente, BandaEntrada) and isinstance(i, Paquete):
                    print("Mover paquete-------")
        
        if len(self.recorrido) > 0:
            self.dirigirse(self.recorrido[0], lista_de_vecinos)



    def advance(self):
            # RobotDeCarga.posiciones[self.unique_id][1] = self.pos
            if not self.sig_pos:
                self.sig_pos = self.pos 
            
            self.model.grid.move_agent(self, self.sig_pos)

"""
CLASES RETO END
"""

"""
Modelo Reto START
"""
class Habitacion(Model):
    robots = []
    def __init__(self, M: int, N: int,
                 num_agentes: int = 4,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',
                 ):

        self.num_agentes = num_agentes
        
        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]


        self.posiciones_estaciones_carga = []
        
        self.posiciones_estantes = [
            [(4, 2), (4, 3), (4, 4), (4, 5), (5, 2), (5, 3), (5, 4), (5, 5)],
            [(4, 9), (4, 10), (4, 11), (4, 12), (5, 9), (5, 10), (5, 11), (5, 12)],
            [(9, 2), (9, 3), (9, 4), (9, 5), (10, 2), (10, 3), (10, 4), (10, 5)],
            [(9, 9), (9, 10), (9, 11), (9, 12), (10, 9), (10, 10), (10, 11), (10, 12)]
        ]

        # Test
        paquete = Paquete(1, self)
        self.grid.place_agent(paquete, (1, 7))

        self.posiciones_bandas = [(True, (1, 7)), (False, (14, 7))]
        

        # Posicionamiento de estantes
        for i in range(len(self.posiciones_estantes)):
            for id, pos in enumerate(self.posiciones_estantes[i]):
                estante = Estante((id+1)*i, self)
                self.grid.place_agent(estante, pos)
                posiciones_disponibles.remove(pos)

        # Posicionamiento bandas
        banda_entrada = BandaEntrada(101, self)
        self.grid.place_agent(banda_entrada, (1, 7))
        self.schedule.add(banda_entrada)
        banda_salida = BandaSalida(1, self)
        self.grid.place_agent(banda_salida, (14, 7))

        # Posicionamiento de robots
        for id in range(self.num_agentes):
            robot = RobotDeCarga(id, self)
            self.grid.place_agent(robot, (0, id))
            self.schedule.add(robot)
            if len(Habitacion.robots) < id+1:
                Habitacion.robots.append(robot)
            else:
                Habitacion.robots[id] = robot

        self.datacollector = DataCollector(
            model_reporters={},
        )
    
    def get_pos_estantes(self):
        return self.posiciones_estantes

    def step(self):

            self.schedule.step()
    
"""
Modelo Reto END
"""