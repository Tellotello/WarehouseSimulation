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
import random

# Creo que dirigirse no esta calculando bien las posiciones

"""
CLASES RETO START
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

def get_pos_cercana(pos, lista_pos):
    distancias_lista = []
    print(f'Se tiene la lista {lista_pos} de la pos {pos}')

    for i in range(len(lista_pos)):
        distancia = round(distancia_entre_puntos(lista_pos[i], pos), 3)
        distancias_lista.append((i, distancia))
    print(f'Se redujo a {distancias_lista}')
    # Asignar sig_pos solo si se encontraron vecinos que cumplan la condicion
    if len(distancias_lista) > 0:
        index_min_distancia = min(distancias_lista, key=lambda x: x[1])[0]
        min_distancia = lista_pos[index_min_distancia]
    # print(f'Se dirige a {pos} mediante {min_distancia}')
        return min_distancia
    return pos

def veces_repetido(elemento, lista):
    se_repite = 0
    for i in lista:
        if i == elemento:
            se_repite += 1
    return se_repite




    
M = N = 15

class Estante(Agent):
    def __init__(self, unique_id, model, tipo):
        super().__init__(unique_id, model)
        self.tipo = tipo 
        self.ocupado = False
    
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
        pos_robots = []
        for i in Habitacion.robots:
            if self.contratado(i.unique_id) != True:
                pos_robots.append(i.pos)
        
        pos_min_distancia = get_pos_cercana(self.pos, pos_robots)

        robot_cercano = get_agentes_pos(self.model, pos_min_distancia)
        for i in robot_cercano:
            if isinstance(i, RobotDeCarga):
                print(f'Se contrato al robot {i.unique_id} que se encuentra a una distancia de {pos_min_distancia} para ir a la pos {self.pos}')
                self.paquetes[-1][1] = i.unique_id # robot contratado
                i.recorrido.append(self.pos)
                print(f'El recorrido del robot {i.unique_id} es {i.recorrido}')
                return 0
            

    
    def paquete_recogido(self, paquete_id):
        for i in self.paquetes:
            if i[0] == paquete_id:
                index_registro_paquete = self.paquetes.index(i)
                self.paquetes.pop(index_registro_paquete)

    def contratado(self, robot_id):
        for i in self.paquetes:
            if i[1] == robot_id:
                return True
        return False



    def step(self):
        print(f'Paquetes: {self.paquetes} de banda {self.unique_id}')
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
    def __init__(self, unique_id, model, tipo):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.tipo = tipo
        self.no_disponible = False
    
    def step(self):
        pass

    def advance(self):
        pass

class Pedido():
    def __init__(self, tipo):
        self.tipo = tipo

class RobotDeCarga(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.recorrido = []
        self.ultimos_10_movs = []

        #Test
        self.instancia_moviendo_paquete = None # Instancia de paquete moviendo
        self.pos_entregar_paquete = None # Pos de estante en donde entregar el paquete

        self.movimientos = list()

    def lista_celdas_vecinas_disponibles(self, pos):
        lista_de_celdas_vecinas = self.model.grid.get_neighborhood(
        self.pos, 
        moore=True,
        include_center=False)

        lista_de_vecinos_agentes = self.model.grid.get_neighbors(
        self.pos, moore=True, include_center=False)

        # Quitar la celdas vecinas que no esten disponibles
        for i in lista_de_vecinos_agentes:
            if isinstance(i, Estante) == True or isinstance(i, BandaEntrada) == True or isinstance(i, BandaSalida) == True:
                index_pos_agente = lista_de_celdas_vecinas.index(i.pos)
                lista_de_celdas_vecinas.pop(index_pos_agente)
        

        return lista_de_celdas_vecinas

    def get_estante_entregar(self, tipo):
        estantes = self.model.get_estantes(tipo)
        posiciones_estantes = []
        for i in estantes:
            posiciones_estantes.append(i.pos)

        pos_estante_cercano = get_pos_cercana(self.pos, posiciones_estantes)
        estante_cercano = get_agentes_pos(self.model, pos_estante_cercano)[0]
        estante_cercano.ocupado = True

        # print(f'Posicion de estante cercano a {self.pos}: {estante_cercano}')
        return pos_estante_cercano


    def recoger_paquete(self, instancia_paquete):
        # print(f'Robot {self.unique_id} recoger_paquete {instancia_paquete.unique_id}')
        self.instancia_moviendo_paquete = instancia_paquete
        # Test
        estante_cercano = self.get_estante_entregar(instancia_paquete.tipo)
        # print(f'robot {self.unique_id} append {estante_cercano}')
        self.recorrido.append(estante_cercano)
        self.pos_entregar_paquete = estante_cercano
        instancia_paquete.no_disponible = True



    def mover_paquete(self, instancia_paquete):
        instancia_paquete.model.grid.move_agent(instancia_paquete, self.sig_pos)

    def entregar_paquete(self, instancia_paquete, instancia_estante):
        instancia_paquete.model.grid.move_agent(instancia_paquete, instancia_estante.pos)
        instancia_paquete.pos = instancia_estante.pos
        print(f'Se eliminara la pos {self.recorrido[0]} del robot {self.unique_id} que se encuentra en {self.pos}')
        self.recorrido.pop(0)
        self.instancia_moviendo_paquete = None
        self.pos_entregar_paquete = None
        self.model.get_banda_entrada().paquete_recogido(instancia_paquete.unique_id)
    
    def posicion_verificada(self, sig_pos, pos_final):
        if sig_pos not in Habitacion.sig_pos_robots and sig_pos != self.movimientos[-2]:
            if sig_pos[1] <= pos_final[1]: 
                if sig_pos[1] >= self.pos[1]:
                    return True
            elif sig_pos[1] >= pos_final[1]:
                if sig_pos[1] <= self.pos[1]:
                    return True
        return False

    def dirigirse(self, pos_final):
        
        self.sig_pos = self.pos
        print(f'------------\nRobot {self.unique_id}')
        print(f'Con recorrido de: {self.recorrido}')

        lista_de_vecinos = self.lista_celdas_vecinas_disponibles(self.pos)
        position_passes = False

        if pos_final:
            if len(self.movimientos) > 5:
                while position_passes != True:
                    pos_cercana = get_pos_cercana(pos_final, lista_de_vecinos)
                    if self.posicion_verificada(pos_cercana, pos_final) != True:
                        index_pos_repetida = lista_de_vecinos.index(pos_cercana)
                        lista_de_vecinos.pop(index_pos_repetida)
                    else:
                        position_passes = True
            else:
                pos_cercana = get_pos_cercana(pos_final, lista_de_vecinos)
            self.sig_pos = pos_cercana
            self.movimientos.append(pos_cercana)
            print(f'Se asigno la pos {self.sig_pos} al robot {self.unique_id}')
            Habitacion.sig_pos_robots[self.unique_id] = self.sig_pos

        # Test Debug
        if len(self.movimientos) > 10:
            if veces_repetido(self.sig_pos, self.movimientos[-10::]) > 2 and len(self.recorrido) == 0 and (7, 7) not in self.recorrido:
                print(f'ATORADO: Robot {self.unique_id} se dirige a {self.sig_pos} con recorrido vacio')
                # coordenada_nueva = (self.recorrido[0][0], self.recorrido[0][1]+1)
                # self.recorrido.insert(0, coordenada_nueva)
            elif veces_repetido(self.sig_pos, self.movimientos[-10::]) > 2 and len(self.recorrido) > 0 and (7, 7) not in self.recorrido:
                print(f'ATORADO: Robot {self.unique_id} se dirige a {self.recorrido[0]} mediante {self.sig_pos}')
                # coordenada_nueva = (self.recorrido[0][0], self.recorrido[0][1]+1)
                # self.recorrido.insert(0, coordenada_nueva)



    def step(self):

        lista_de_vecinos = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True,
            include_center=True)
        print(f'Robot {self.unique_id} con paquete_en_movimiento = {self.instancia_moviendo_paquete}')
        if self.instancia_moviendo_paquete == None:
            # print(f'Vecinos de la pos {self.pos} de agente {self.unique_id}')
            for i in lista_de_vecinos:
                agentes = get_agentes_pos(self.model, i)
                if len(agentes) > 0:
                    for agente in agentes:
                        # print(agente)
                        if isinstance(agente, Paquete):
                            print(f'Es el paquete {agente.unique_id} con no_disponible de: {agente.no_disponible}')
                        if isinstance(agente, Paquete) and agente.no_disponible != True:
                            if len(self.recorrido) > 0:
                                print(f'Se eliminara la pos {self.recorrido[0]} del robot {self.unique_id} que se encuentra en {self.pos}')
                                self.recorrido.pop(0)
                            print(f'El agente {self.unique_id} encontro paquete y lo va a recoger')
                            self.recoger_paquete(agente)
                            break
        elif self.pos_entregar_paquete in lista_de_vecinos:
            agentes_pos_entregar = get_agentes_pos(self.model, self.pos_entregar_paquete)
            for i in agentes_pos_entregar:
                if isinstance(i, Estante):
                    self.entregar_paquete(self.instancia_moviendo_paquete, i)
                    break

        
        if len(self.recorrido) > 0:
            self.dirigirse(self.recorrido[0])



    def advance(self):
        if not self.sig_pos:
            self.sig_pos = self.pos

        self.model.grid.move_agent(self, self.sig_pos)
        if self.instancia_moviendo_paquete:
            self.mover_paquete(self.instancia_moviendo_paquete)
            
                

"""
CLASES RETO END
"""

"""
Modelo Reto START
"""
class Habitacion(Model):
    robots = []
    #Test
    sig_pos_robots = []
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
        # Hacer una lista de paquetes y cuando se recoja uno que se ponga otro y se tenga que contratar a otro robot
            # Con tipo de entero random range(len(self.posicones_estantes))
        # paquete = Paquete(1, self, 2)
        # self.grid.place_agent(paquete, (1, 7))
        self.index_paquete = 1000

        self.posiciones_bandas = [(True, (1, 7)), (False, (14, 7))]
        

        # Posicionamiento de estantes
        for i in range(len(self.posiciones_estantes)):
            for id, pos in enumerate(self.posiciones_estantes[i]):
                estante = Estante((id+1)*i, self, i)
                self.grid.place_agent(estante, pos)
                posiciones_disponibles.remove(pos)

        # Posicionamiento bandas
        banda_entrada = BandaEntrada(101, self)
        self.grid.place_agent(banda_entrada, (1, 7))
        self.schedule.add(banda_entrada)
        banda_salida = BandaSalida(102, self)
        self.grid.place_agent(banda_salida, (14, 7))

        # Posicionamiento de robots
        for id in range(self.num_agentes):
            robot = RobotDeCarga(id, self)
            self.grid.place_agent(robot, (0, id))
            self.schedule.add(robot)
            Habitacion.sig_pos_robots.append((0, 0))
            if len(Habitacion.robots) < id+1:
                Habitacion.robots.append(robot)
            else:
                Habitacion.robots[id] = robot

        self.datacollector = DataCollector(
            model_reporters={},
        )
    
    
    def get_estantes(self, tipo):
        """
        Get instancias de estantes disponibles
        en base al tipo.
        """
        estantes_disponibles = []
        for i in self.posiciones_estantes[tipo]:
            estante = get_agentes_pos(self, i)[0]
            if estante.ocupado != True:
                estantes_disponibles.append(estante)
        return estantes_disponibles
    
    def get_banda_entrada(self):
        return get_agentes_pos(self, self.posiciones_bandas[0][1])[0]

    def step(self):
        agentes_banda = get_agentes_pos(self, self.posiciones_bandas[0][1])
        hay_paquete = False
        for i in agentes_banda:
            if isinstance(i, Paquete):
                hay_paquete = True
                break
        if hay_paquete != True:
            paquete = Paquete(self.index_paquete, self, random.randint(0, 3))
            self.grid.place_agent(paquete, self.posiciones_bandas[0][1])
            self.schedule.add(paquete)
            print(f'Se posicino paquete {self.index_paquete}')
            self.index_paquete += 1
        self.schedule.step()
    
"""
Modelo Reto END
"""