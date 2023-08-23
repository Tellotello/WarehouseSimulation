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
        return distance
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
    

    def hay_paquete(self):
        agentes_banda = get_agentes_pos(self.model, self.pos)
        hay_paquete = False
        for i in agentes_banda:
            if isinstance(i, Paquete):
                hay_paquete = True
                break
        return hay_paquete
    

    
    def contratar_robot_recoger(self):
        for i in RobotDeCarga.posiciones:
            distancias_robots = [(i[1], distancia_entre_puntos(self.pos, i[1]))]
        
        indice_min_distancia = min(distancias_robots, key=lambda x: x[1])[0]
        robot_cercano = get_agentes_pos(self.model, distancias_robots[indice_min_distancia][0])
        robot_cercano.recorrido.append(self.pos)



    def step(self):

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
    posiciones = [(0,(1,0))]
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.recorrido = []
        RobotDeCarga.posiciones.append((self.unique_id, self.pos))

    def dirigirse(self, pos_final, lista_de_vecinos):
        distancias_vecinos = []
        for i in range(len(lista_de_vecinos)):
            # Que no sea mueble ni este en celdas limpias
            agente_vecino = self.get_agente_from_pos(lista_de_vecinos[i].pos)

            if isinstance(agente_vecino, Estante) != True and isinstance(agente_vecino, BandaEntrada) != True and isinstance(agente_vecino, BandaSalida) != True:
                distancia = round(distancia_entre_puntos(agente_vecino.pos, pos_final), 3)
                distancias_vecinos.append((i, distancia))


        index_min_distancia = min(distancias_vecinos, key=lambda x: x[1])[0]
        min_distancia = lista_de_vecinos[index_min_distancia]
        self.sig_pos = min_distancia.pos


    def step(self):
        lista_de_vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        for i in lista_de_vecinos:
            if isinstance(i, BandaEntrada) and isinstance(i, Paquete):
                print("Mover paquete")
        
        if len(self.recorrido) > 0:
            self.dirigirse(self.recorrido[0])



    def advance(self):
            RobotDeCarga.posiciones[self.unique_id][1] = self.pos
            self.model.grid.move_agent(self, self.sig_pos)

"""
CLASES RETO END
"""


class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad

class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

# Clase de agente estación de carga
class EstacionDeCarga(Agent):
    posiciones = []
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = False
        if len(EstacionDeCarga.posiciones) <= unique_id:
            EstacionDeCarga.posiciones.append(self.pos)

            
        # if isinstance(self.enCarga, RobotLimpieza):
        #     self.enCarga.carga = 100
        #     self.ocupada = False

class RobotLimpieza(Agent):

    funcionando = []
    celdas_limpias = []
    busca_contrato = -1
    contratos = []
    contratado = -1

    def __init__(self, unique_id, model, mueblesPos, recorrido):
        super().__init__(unique_id, model)
        self.prendido = True
        self.mueblesPos = mueblesPos
        self.sig_pos = None
        self.movimientos = list()
        self.movimientos_recorrido = list()
        self.carga = 100
        self.recorrido = recorrido
        self.estacion_de_carga = None
        RobotLimpieza.funcionando.append(self.unique_id)


    
    def get_agente_from_pos(self, pos):
        agente = self.model.grid.get_cell_list_contents([pos])[0]
        return agente

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos
        RobotLimpieza.celdas_limpias.append(celda_a_limpiar.pos)

    def cargar(self):

        if self.estacion_de_carga == None:
            distancias_carga = []
            posiciones = Habitacion.pos_estaciones_carga(self.model)
            estaciones = []
            for i in posiciones:
                estacion_carga = self.model.grid.get_cell_list_contents([i])[0]
                estaciones.append(estacion_carga)
                distancia = self.get_distance(self.pos, i)
                if estacion_carga.ocupada == True:
                    distancias_carga.append(distancia*1000)
                else:
                    distancias_carga.append(distancia)
                
            if len(distancias_carga) == 0:
                return 0
            else:
                min_index = distancias_carga.index(min(distancias_carga))
                self.estacion_de_carga = posiciones[min_index]
                estaciones[min_index].ocupada = True
        elif self.pos == self.estacion_de_carga:
            estacion_carga = self.model.grid.get_cell_list_contents([self.estacion_de_carga])[0]
            self.carga += 25
            if self.carga < 100:
                self.sig_pos = self.pos
            if self.carga > 100:
                self.carga = 100
                self.estacion_de_carga = None
                Habitacion.agregar_recarga(self.model)
        elif self.pos == self.estacion_de_carga and self.carga > 90:
            self.estacion_de_carga = None
            estacion_carga = self.model.grid.get_cell_list_contents([self.estacion_de_carga])[0]
            estacion_carga.ocupada = False
        elif self.estacion_de_carga:
            lista_de_vecinos = self.model.grid.get_neighbors(
                self.pos, moore=True, include_center=False)
            self.dirigirse(self.estacion_de_carga, lista_de_vecinos)

    def dirigirse(self, pos_final, lista_de_vecinos):
        distancias_vecinos = []
        for i in range(len(lista_de_vecinos)):
            # Que no sea mueble ni este en celdas limpias
            agente_vecino = self.get_agente_from_pos(lista_de_vecinos[i].pos)

            if isinstance(agente_vecino, Mueble) != True and isinstance(agente_vecino, RobotLimpieza) != True and lista_de_vecinos[i].pos in self.movimientos_recorrido:
                distancia = round(self.get_distance(agente_vecino.pos, pos_final), 3)
                distancias_vecinos.append((i, distancia))

        for i in range(len(lista_de_vecinos)):
            # Que no sea mueble ni este en celdas limpias
            agente_vecino = self.get_agente_from_pos(lista_de_vecinos[i].pos)
            if isinstance(agente_vecino, Mueble) != True and isinstance(agente_vecino, RobotLimpieza) != True:
                distancia = round(self.get_distance(agente_vecino.pos, pos_final), 3)
                distancias_vecinos.append((i, distancia))


        index_min_distancia = min(distancias_vecinos, key=lambda x: x[1])[0]
        min_distancia = lista_de_vecinos[index_min_distancia]
        self.sig_pos = min_distancia.pos
        
        if len(self.movimientos) > 1:
            if self.sig_pos in self.movimientos[-2::]:
                print("sacamos una pos")
                if len(self.recorrido) > 0:
                    self.recorrido.pop(0)
                
    def seleccionar_nueva_pos(self, lista_de_vecinos):
        # print(self.recorrido)
        if len(self.recorrido) > 0:
            if self.pos == self.recorrido[0]:
                self.movimientos_recorrido.append(self.recorrido[0])
                self.recorrido.pop(0)
                for i in lista_de_vecinos:
                    if isinstance(i, EstacionDeCarga) and self.carga < 80:
                        self.cargar()
                if len(self.recorrido) > 0:
                    while(isinstance(self.get_agente_from_pos(self.recorrido[0]), Mueble)):
                        self.recorrido.pop(0)
                        if(len(self.recorrido) == 0):
                            break
                
            if len(self.recorrido) > 0:
                self.dirigirse(self.recorrido[0], lista_de_vecinos)

    def get_distance(self, p1, p2):
        term_x = (p2[0] - p1[0])**2
        term_y = (p2[1] - p1[1])**2
        distance = math.sqrt(term_x + term_y)
        return distance



    # Hace el metodo publico
    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        # #Opción 1
        # return [vecino for vecino in lista_de_vecinos
        #                 if isinstance(vecino, Celda) and vecino.sucia]
        # #Opción 2
        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
                
        return celdas_sucias
    

    def step(self):

        lista_de_vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
    
        

        if RobotLimpieza.busca_contrato == self.unique_id:
            # Encontrar el mayor contrato
            if len(RobotLimpieza.contratos) > 0:
                lens_contratos = [len(i[1]) for i in RobotLimpieza.contratos]
                index_mayor_contrato = lens_contratos.index(max(lens_contratos))
                contrato = RobotLimpieza.contratos[index_mayor_contrato][1]
                RobotLimpieza.contratado = RobotLimpieza.contratos[index_mayor_contrato][0]

                #Agregar mitad de contrato a tu recorrido
                self.recorrido.extend(contrato[len(contrato)//2::])
                print(f'Contrato: {contrato}\nExtend part: {self.recorrido}')
                RobotLimpieza.contratos = []
                RobotLimpieza.busca_contrato = -1
            
            #Quitar esa parte del otro agente
        elif RobotLimpieza.busca_contrato == self.unique_id and len(RobotLimpieza.contratos) == 0:
            self.prendido = False
        elif RobotLimpieza.contratado == self.unique_id:
            if len(self.recorrido) > 2:
                self.recorrido = self.recorrido[::len(self.recorrido)//2]
            RobotLimpieza.contratado = -1
        # Subir contrato
        elif RobotLimpieza.busca_contrato != -1 and len(self.recorrido) > 2:
            RobotLimpieza.contratos.append((self.unique_id, self.recorrido))

        elif len(self.recorrido) == 0 and RobotLimpieza.busca_contrato == -1:
            RobotLimpieza.busca_contrato = self.unique_id
        elif self.estacion_de_carga != None:
            self.cargar()
        else: 

            celdas_sucias = self.buscar_celdas_sucia(lista_de_vecinos)

            if len(celdas_sucias) == 0:
                if self.carga < 30:
                    self.cargar()
                else:

                    self.seleccionar_nueva_pos(lista_de_vecinos)
            else:
                self.limpiar_una_celda(celdas_sucias)
                # self.seleccionar_nueva_pos(lista_de_vecinos)



    def advance(self):
        if self.pos != self.sig_pos:    
            self.movimientos.append(self.sig_pos)
            Habitacion.agregar_movimiento(self.model)
        if self.prendido == False:
            self.sig_pos = self.pos
            self.model.grid.move_agent(self, self.sig_pos)
        elif self.carga > 0:
            self.carga -= 1
            Habitacion.agregar_uso_energia(self.model)
            self.model.grid.move_agent(self, self.sig_pos)

"""
Modelo Reto START
"""
class Habitacion(Model):
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


        for id in range(self.num_agentes):
            robot = RobotDeCarga(id, self)
            self.grid.place_agent(robot, (0, id))
            self.schedule.add(robot)

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