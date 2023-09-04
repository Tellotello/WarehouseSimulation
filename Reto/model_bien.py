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
import requests

# Creo que dirigirse no esta calculando bien las posiciones

"""
CLASES RETO START
"""
def registrar_log(message):
    """
    Funcion para debug
    """
    # with open("log.txt", 'a') as log:
    #     log.write(message)
    #     log.close()
    pass



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

    for i in range(len(lista_pos)):
        distancia = distancia_entre_puntos(lista_pos[i], pos)
        distancias_lista.append((i, distancia))

    # Asignar sig_pos solo si se encontraron vecinos que cumplan la condicion
    if len(distancias_lista) > 0:
        index_min_distancia = min(distancias_lista, key=lambda x: x[1])[0]
        min_distancia = lista_pos[index_min_distancia]
        return min_distancia
    return pos

# def veces_repetido(elemento, lista):
#     se_repite = 0
#     for i in lista:
#         if i == elemento:
#             se_repite += 1
#     return se_repite


class Pedido():
    def __init__(self, id, tipo):
        self.id = id
        self.tipo = tipo

class Actividad():
    def __init__(self, tipo_actividad, pos_final, tipo_pedido=None, id_pedido=None):
        self.tipo_actividad = tipo_actividad
        self.pos_final = pos_final
        self.tipo_pedido = tipo_pedido
        self.id_pedido = id_pedido

class ContratoPaquete():
    def __init__(self, id_robot, id_paquete=None, tipo_pedido=None, id_pedido=None):
        self.id_paquete = id_paquete
        self.id_robot = id_robot
        self.tipo_pedido = tipo_pedido
        self.id_pedido = id_pedido


# class ContratoPedido():
#     def __init__(self, id_paquete, id_robot, tipo):
#         self.id_paquete = id_paquete
#         self.id_robot = id_robot
#         self.tipo


    
M = N = 15

class Estante(Agent):
    def __init__(self, unique_id, model, tipo):
        super().__init__(unique_id, model)
        self.tipo = tipo 
        self.lleno = False
        self.cant_paquetes = 0
        self.pos = None
  
    def step(self):
        if self.cant_paquetes >= 2:
            self.lleno = True
        else:
            self.lleno = False
    
    def getNumPaquetes(self):
        return self.cant_paquetes
    
class BandaSalida(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # Se registran los paquetes en forma de (self, id_paquete, id_robot, tipo_pedido=None)
        self.contratos_pedidos = []
    


    def hay_pedido(self):
        # for i in self.contratos_pedidos:
        for i in self.model.pedidos:
            ids_pedidos_registrados = [n.id_pedido for n in self.contratos_pedidos]
            if i.id not in ids_pedidos_registrados:
                return True
        return False
        
    def registrar_pedidos(self):
        """
        Por cada pedido de self.model.pedidos,
        si su id no esta registrado, agregarlo 
        como contrato sin robot.
        """
        for i in self.model.pedidos:
            if self.pedido_registrado(i.id) != True:
                registrar_log(f'\nSe registra pedido')
                nuevo_contrato = ContratoPaquete(id_robot=-1, id_pedido=i.id, tipo_pedido=i.tipo)
                self.contratos_pedidos.append(nuevo_contrato)
                    
    
    def pedido_registrado(self, id):
        for i in self.contratos_pedidos:
            if i.id_pedido == id:
                return True
        return False

    def hay_disponible(self, tipo):
        posiciones_estantes = self.model.posiciones_estantes[tipo]
        cuenta = 0
        for i in posiciones_estantes:
            agentes = get_agentes_pos(self.model, i)
            for n in agentes:
                if isinstance(n, Paquete) and n.tipo == tipo:
                    cuenta += 1
                    # return True
        if cuenta > 3:
            return True
        else:
            return False
        # return False



    def contratar_robot_entregar(self, tipo, id_pedido):
        pos_robots = []
        for i in Habitacion.robots:
            # if i.ocupado == False:
            #     pos_robots.append(i.pos)
            # if len(i.actividades) < 3 and i.ocupado == False:
            if  i.ocupado == False:
                pos_robots.append(i.pos)
        if pos_robots:
        
            
            pos_min_distancia = get_pos_cercana(self.pos, pos_robots)

            robot_cercano = get_agentes_pos(self.model, pos_min_distancia)
            for i in robot_cercano:
                if isinstance(i, RobotDeCarga):
                    # n.id_robot = i.unique_id
                    # self.paquetes[-1].id_robot = i.unique_id # robot contratado
                    # i.recorrido += i.a_star_path(i.pos, self.pos)
                    # id_paquete, pos_paquete = i.get_paquete_cercano(n.tipo_pedido)
                    # recoger_act = Actividad(3, pos_paquete, id_paquete)
                    entregar_act = Actividad(4, self.pos, tipo, id_pedido=id_pedido)
                    # i.actividades.append(recoger_act)
                    i.actividades.append(entregar_act)
                    return i.unique_id
            

    
    def pedido_entregado(self, paquete_id, id_pedido):
            for i in range(len(self.contratos_pedidos)):
                if self.contratos_pedidos[i].id_pedido == id_pedido:
                    self.contratos_pedidos.pop(i)
                    break
                            #Remover de pedidos en modelo
                for i, p in enumerate(self.model.pedidos):
                    if p.id == id_pedido:
                        self.model.pedidos.pop(i)
            # agentes_banda = get_agentes_pos(self.model, self.pos)

            #Test
            # for n in agentes_banda:
            #     if isinstance(n, Paquete) and n.unique_id == paquete_id:
            #         self.model.grid.remove_agent(n)
            #         self.model.schedule.remove(n)
            #         #Remover de pedidos en modelo
            #         for i, p in enumerate(self.model.pedidos):
            #             if p.id == id_pedido:
            #                 self.model.pedidos.pop(i)
                            

    def contratado(self, robot_id):
        for i in self.contratos_pedidos:
            if i.id_robot == robot_id:
                return True
        return False



    def step(self):
        agentes_banda = get_agentes_pos(self.model, self.pos)

        # Test
        for n in agentes_banda:
            if isinstance(n, Paquete):
                self.model.grid.remove_agent(n)
                self.model.schedule.remove(n)

                            
        
        if self.hay_pedido():
            registrar_log(f'\nHay pedido')
            self.registrar_pedidos()
        if self.contratos_pedidos:
            #Test
            registrar_log("\nPEDIDOS:")
            for i in self.contratos_pedidos:
                registrar_log(f'\nPedido_id: {i.id_pedido}, tipo_pedido:{i.tipo_pedido}, id_robot: {i.id_robot}')
                if i.id_robot == -1 and self.hay_disponible(i.tipo_pedido):
                    registrar_log(f"\nEl viejo id_robot del pedido {i.id_pedido} es {i.id_robot}")
                    i.id_robot = self.contratar_robot_entregar(i.tipo_pedido, i.id_pedido)
                    registrar_log(f"\nEl nuevo id_robot del pedido {i.id_pedido} es {i.id_robot}")


class BandaEntrada(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # Se registran los paquetes en forma de (id del paquete, id del robot contratado)
        self.paquetes = []
    

    def hay_paquete(self):
        for i in self.paquetes:
            if i.id_robot == -1:
                return True
        return False
        
    def registrar_paquetes(self):
        agentes_banda = get_agentes_pos(self.model, self.pos)
        for i in agentes_banda:
                if isinstance(i, Paquete) and self.paquete_registrado(i.unique_id) != True:
                    nuevo_contrato = ContratoPaquete(id_robot=-1, id_paquete=i.unique_id)
                    # self.paquetes.append([i.unique_id, -1])
                    self.paquetes.append(nuevo_contrato)
                    
    
    def paquete_registrado(self, id):
        for i in self.paquetes:
            if i.id_paquete == id:
                return True
        return False

    
    def contratar_robot_recoger(self):
        pos_robots = []
        for i in Habitacion.robots:
            # if i.ocupado == False and len(i.actividades) < 3:
            if i.ocupado == False:
                pos_robots.append(i.pos)
        if pos_robots:
            
            pos_min_distancia = get_pos_cercana(self.pos, pos_robots)

            robot_cercano = get_agentes_pos(self.model, pos_min_distancia)
            for i in robot_cercano:
                if isinstance(i, RobotDeCarga):
                    self.paquetes[-1].id_robot = i.unique_id # robot contratado
                    # i.recorrido += i.a_star_path(i.pos, self.pos)
                    nueva_actividad = Actividad(1, self.pos)
                    i.actividades.append(nueva_actividad)
                    break
            

    
    def paquete_recogido(self, paquete_id):

        # for i in range(len(self.paquetes)):
        #     if self.paquetes[i].id_paquete == paquete_id:
        #         self.paquetes.pop(i)
        for i in self.paquetes:
            if i.id_paquete == paquete_id:
                index_paquete = self.paquetes.index(i)
                self.paquetes.pop(index_paquete)

    def contratado(self, robot_id):
        for i in self.paquetes:
            if i.id_robot == robot_id:
                return True
        return False



    def step(self):
        self.registrar_paquetes()
        if self.hay_paquete():
            self.contratar_robot_recoger()

        
class EstacionDeCarga(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.ocupada = False



class Paquete(Agent):
    def __init__(self, unique_id, model, tipo):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.tipo = tipo
        self.disponible = True



    

class RobotDeCarga(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.recorrido = []
        self.ocupado = False
        self.id_paquete_recoger = None

        #Test
        self.instancia_moviendo_paquete = None # Instancia de paquete moviendo
        # Sistema de actividades
        # 1. Recoger y guardar paquete
        # 2. Recoger y entregar paquete de pedido
        # 3. Cargarse7
        # clase de Actividad(id_act, pos_final)
        self.actividades = []

        # self.movimientos = list()

    def lista_celdas_vecinas_disponibles(self, pos):
        lista_de_celdas_vecinas = self.model.grid.get_neighborhood(
        pos, 
        moore=True,
        include_center=False)

        lista_de_vecinos_agentes = self.model.grid.get_neighbors(
        pos, moore=True, include_center=False)

        # Quitar la celdas vecinas que no esten disponibles
        for i in lista_de_vecinos_agentes:
            if isinstance(i, Estante) == True or isinstance(i, BandaEntrada) == True or isinstance(i, BandaSalida) == True:
                if i.pos in lista_de_celdas_vecinas:
                    index_pos_agente = lista_de_celdas_vecinas.index(i.pos)
                    lista_de_celdas_vecinas.pop(index_pos_agente)
        

        return lista_de_celdas_vecinas

    def get_estante_entregar(self, tipo):
        estantes = self.model.get_estantes(tipo)
        registrar_log(f'\nSe tienen {len(estantes)} estantes de tipo {tipo}')
        posiciones_estantes = []
        for i in estantes:
            posiciones_estantes.append(i.pos)
        
        if posiciones_estantes:

            pos_estante_cercano = get_pos_cercana(self.pos, posiciones_estantes)
            agentes_estante_cercano = get_agentes_pos(self.model, pos_estante_cercano)
            for a in agentes_estante_cercano:
                if isinstance(a, Estante):
                    a.cant_paquetes += 1
                    return pos_estante_cercano
            # estante_cercano.lleno = True
        else: 
            return None
    

    def get_paquete_cercano(self, tipo):
        # estantes = self.model.get_estantes(tipo)
        pos_estantes = self.model.posiciones_estantes[tipo]

        paquetes_cercanos = []
        for i in pos_estantes:
            agentes_estante = get_agentes_pos(self.model, i)
            for n in agentes_estante:
                if isinstance(n, Paquete) and n.disponible:
                    paquetes_cercanos.append(n)
        pos_paquetes_cercanos = [q.pos for q in paquetes_cercanos]
        registrar_log(f'\n Pos paquetes tipo {tipo}: {[m.unique_id for m in paquetes_cercanos]}')

        pos_paquete_cercano = get_pos_cercana(self.pos, pos_paquetes_cercanos)
        # paquete_cercano = get_agentes_pos(self.model, pos_paquete_cercano)
        index_paquete_cercano = pos_paquetes_cercanos.index(pos_paquete_cercano)
        paquete_cercano = paquetes_cercanos[index_paquete_cercano]
        id_paquete = paquete_cercano.unique_id
        paquete_cercano.disponible = False

        agentes_pos = get_agentes_pos(self.model, pos_paquete_cercano)
        # id_paquete = None
        for p in agentes_pos:
            if isinstance(p, Estante):
                p.cant_paquetes -= 1
        
        return id_paquete, pos_paquete_cercano


    def recoger_paquete_banda(self, instancia_paquete):
        registrar_log(f"\nEl robot {self.unique_id} entro a recoger_paquete_banda instancia parametro {type(instancia_paquete)}, instancia self {type(self.instancia_moviendo_paquete)}")
        self.instancia_moviendo_paquete = instancia_paquete
        estante_cercano = self.get_estante_entregar(instancia_paquete.tipo)
        # self.recorrido += self.a_star_path(self.pos, estante_cercano)
        # Actividad de tipo 2: Almacenar paquete en estante
        actividad_nueva = Actividad(2, estante_cercano)
        self.actividades.append(actividad_nueva)
        self.actividades.pop(0)
        instancia_paquete.disponible = False
        self.ocupado = True
        registrar_log(f"\nEl robot {self.unique_id} final de recoger_paquete_banda instancia parametro {type(instancia_paquete)}, instancia self {type(self.instancia_moviendo_paquete)}")
    # test

    def recoger_paquete_estante(self, instancia_paquete, instancia_estante):
        self.instancia_moviendo_paquete = instancia_paquete
        if self.actividades[0].tipo_actividad == 3:
            self.actividades.pop(0)
        instancia_estante.cant_paquetes -= 1
        instancia_paquete.disponible = False
        self.ocupado = True
        self.id_paquete_recoger = None
        # instancia_estante.ocupado = False


    def mover_paquete(self, instancia_paquete):
        instancia_paquete.model.grid.move_agent(instancia_paquete, self.sig_pos)

    def entregar_paquete_estante(self, instancia_paquete, pos_estante):
        registrar_log(f"\nEl robot {self.unique_id} entro a entregar_paquete_estante instancia parametro {type(instancia_paquete)}, instancia self {type(self.instancia_moviendo_paquete)}")
        # registrar_log(f'Tipo_paquiete: {instancia_paquete.tipo}')
        # self.model.grid.move_agent(instancia_paquete, pos_estante)
        if instancia_paquete:
            instancia_paquete.model.grid.move_agent(instancia_paquete, pos_estante)
            instancia_paquete.disponible = True
            self.model.get_banda_entrada().paquete_recogido(instancia_paquete.unique_id)
        # instancia_paquete.pos = instancia_estante.pos
        self.instancia_moviendo_paquete = None
        self.actividades.pop(0)
        self.ocupado = False
        registrar_log(f"\nEl robot {self.unique_id} final de entregar_paquete_estante y la instancia parametro es {type(instancia_paquete)} y la instancia self es {self.instancia_moviendo_paquete}")


    def entregar_paquete_banda(self, instancia_paquete, coord_banda, id_pedido):
        self.instancia_moviendo_paquete = None
        # Test
        if instancia_paquete:
            instancia_paquete.model.grid.move_agent(instancia_paquete, coord_banda)
            self.model.get_banda_salida().pedido_entregado(instancia_paquete.unique_id, id_pedido)
        if self.actividades[0].tipo_actividad == 4 and self.actividades[0].id_pedido == id_pedido:
            self.actividades.pop(0)
        self.ocupado = False



    # A Star Algo
    def a_star_path(self, pos_inicial, pos_final):
        if pos_inicial == pos_final:
            return []
        
        class Node():
            def __init__(self, coord, g_cost, h_cost, viene_de):
                self.coord = coord
                self.g_cost = g_cost
                self.h_cost = h_cost
                self.f_cost = g_cost + h_cost
                self.viene_de = viene_de

        class Queue():
            def __init__(self):
                self.queue = []
            
            def push(self, node):
                if len(self.queue) == 0:
                    self.queue.append(node)
                else:
                    for i in range(len(self.queue)):
                        if i == len(self.queue)-1:
                            self.queue.append(node)
                        elif self.queue[i].f_cost < node.f_cost:
                            self.queue.insert(i, node)
                            break
            
            def pop(self):
                self.queue.pop()
            
            def get_head(self):
                return self.queue[-1]
            
            def get_size(self):
                return len(self.queue)
            


        nodo_actual = Node(pos_inicial, 0, 0, None)
        open = Queue()
        open.push(nodo_actual)
        pos_encontrada = False
        closed = list()

        pos_visitadas = []
        while pos_encontrada != True:
            lista_de_celdas_vecinas = self.model.grid.get_neighborhood(
            nodo_actual.coord, 
            moore=True,
            include_center=True)

            if pos_final in lista_de_celdas_vecinas or distancia_entre_puntos(nodo_actual.coord, pos_final) < 2:
                pos_encontrada = True
                break

            open.pop()
            lista_vecinos = self.lista_celdas_vecinas_disponibles(nodo_actual.coord)   

            for i in lista_vecinos:
                if i not in pos_visitadas:
                    g_cost = nodo_actual.g_cost+1
                    h_cost = distancia_entre_puntos(i, pos_final)
                    vertice = Node(i, g_cost, h_cost, nodo_actual)
                    open.push(vertice)
                    pos_visitadas.append(i)
                    # for n in closed:
                    #     if n.coord == i and n.f_cost > vertice.f_cost:
                    #         n = vertice
                    #         break
            nodo_actual = open.get_head()
            closed.append(nodo_actual)


        camino = []
        while nodo_actual.coord != pos_inicial:
            camino.insert(0, nodo_actual.coord)
            nodo_actual = nodo_actual.viene_de

        return camino
            

        
    def step(self):

        registrar_log(f'\n El robot {self.unique_id} se encuentra en {self.pos}, ocupado de: {self.ocupado}, con recorrido de {self.recorrido}, instancia_paquete: {type(self.instancia_moviendo_paquete)} y {len(self.actividades)} actividades')
        registrar_log(f'\nACTIVIDADES Robot {self.unique_id}')
        for a in self.actividades:
            registrar_log(f'\n id_act: {a.tipo_actividad}, pos_final: {a.pos_final}, tipo_pedido: {a.tipo_pedido}, id_pedido: {a.id_pedido}')
        # No Estan ocupados
        # no tienen recorrido
        lista_de_vecinos = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True,
            include_center=True)

        if len(self.actividades) == 0:
            self.sig_pos = self.pos
        else:
            actividad_actual = self.actividades[0]

            # Si la posicion final de la actividad esta en los vecinos
            # elif actividad_actual.tipo_actividad == 4 and self.instancia_moviendo_paquete == None and len(self.recorrido) == 0:
            if actividad_actual.tipo_actividad == 4 and self.instancia_moviendo_paquete == None and len(self.recorrido) == 0:
            # if actividad_actual.tipo_actividad == 4 and self.id_paquete_recoger == None:
                if self.model.get_banda_salida().hay_disponible(actividad_actual.tipo_pedido):
                    id_paquete, pos_paquete = self.get_paquete_cercano(actividad_actual.tipo_pedido)
                    registrar_log("\n=======Entre a la condicion rara")
                    registrar_log(f'\nid_paquete: {id_paquete}, pos_paquete: {pos_paquete}, tipo: {actividad_actual.tipo_pedido}, pos_actual: {self.pos}')
                    self.id_paquete_recoger = id_paquete
                    actividad_recoger = Actividad(3, pos_paquete, actividad_actual.tipo_pedido)
                    self.ocupado= True
                    self.actividades.insert(0, actividad_recoger)

            elif actividad_actual.pos_final in lista_de_vecinos:
                # Hacer el if-elif largo con los pasos para cada actividad

                # Recoger paquete de BandaEntrada
                if actividad_actual.tipo_actividad == 1:
                        agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                        if len(agentes) > 0:
                            for agente in agentes:
                                if isinstance(agente, Paquete) and agente.disponible == True:
                                    # if len(self.recorrido) > 0:
                                    #     self.recorrido.pop(0)
                                    registrar_log(f'\ntypo_agente_2: {type(agente) }')
                                    self.recoger_paquete_banda(agente)
                                    break
                # Almacenar paquete en estante
                elif actividad_actual.tipo_actividad == 2:
                    agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                    if len(agentes) > 0:
                        for agente in agentes:
                            if isinstance(agente, Estante):
                                registrar_log(f'\ntipo_paquete: {type(self.instancia_moviendo_paquete)}')
                                self.entregar_paquete_estante(self.instancia_moviendo_paquete, actividad_actual.pos_final)
                                break
                # Recoger paquete de estante       
                elif actividad_actual.tipo_actividad == 3:
                    agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                    instancia_estante = None
                    instancia_paquete = None
                    registrar_log(f'\nAGENTES en {actividad_actual.pos_final}')
                    for n in agentes:
                        registrar_log(f'\nTipo de agente: {type(n)}')
                        if isinstance(n, Paquete) and n.unique_id == self.id_paquete_recoger:
                            registrar_log("\nSe encontro paquete")
                            instancia_paquete = n
                        elif isinstance(n, Estante):
                            instancia_estante = n
                        if instancia_paquete and instancia_estante:
                            self.recoger_paquete_estante(instancia_paquete, instancia_estante)

                # Entregar paquete en BandaSalida 
                elif actividad_actual.tipo_actividad == 4 and self.instancia_moviendo_paquete:
                    agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                    if len(agentes) > 0:
                        for agente in agentes:
                            if isinstance(agente, BandaSalida):
                                self.entregar_paquete_banda(self.instancia_moviendo_paquete, agente.pos, id_pedido=actividad_actual.id_pedido)
                                break
            
            elif len(self.recorrido) == 0:
                registrar_log(f'\nSe agrego a recorrido con act actual de tipo: {actividad_actual.tipo_actividad}')
                registrar_log(f'\nCamino de {self.pos} a {actividad_actual.pos_final}')
                registrar_log(f'\nAntes recorrido era {self.recorrido}')
                recorrido_actividad = self.a_star_path(self.pos, actividad_actual.pos_final)
                registrar_log(f'\nSe calculo el camino {recorrido_actividad}')
                self.recorrido += recorrido_actividad
                registrar_log(f'\nAhora recorrido es {self.recorrido}')
                #  
             

        if self.actividades:
            self.ocupado = True
        else:
            self.ocupado = False

        if len(self.recorrido) == 0:
            self.sig_pos = self.pos

        else:
            self.sig_pos = self.recorrido[0]
            self.recorrido.pop(0)




    def advance(self):
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

        self.current_step_data = {}  # Dictionary to hold current step data

        self.num_agentes = num_agentes
        
        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]


        self.posiciones_estaciones_carga = []
        self.pedidos = []
        
        self.posiciones_estantes = [
            [(4, 2), (4, 3), (4, 4), (4, 5), (5, 2), (5, 3), (5, 4), (5, 5)],
            [(4, 9), (4, 10), (4, 11), (4, 12), (5, 9), (5, 10), (5, 11), (5, 12)],
            [(9, 2), (9, 3), (9, 4), (9, 5), (10, 2), (10, 3), (10, 4), (10, 5)],
            [(9, 9), (9, 10), (9, 11), (9, 12), (10, 9), (10, 10), (10, 11), (10, 12)]
        ]

        # Test
        # Hacer una lista de paquetes y cuando se recoja uno que se ponga otro y se tenga que contratar a otro robot
            # Con tipo de entero random range(len(self.posicones_estantes))
        paquete = Paquete(1, self, 2)
        # self.grid.place_agent(paquete, (0, 7))
        self.index_paquete = 1000

        self.posiciones_bandas = [(True, (0, 7)), (False, (14, 7))]
        

        # Posicionamiento de estantes
        for i in range(len(self.posiciones_estantes)):
            for id, pos in enumerate(self.posiciones_estantes[i]):
                estante = Estante((10000+i)*(id+1), self, i)
                estante.pos = pos
                self.grid.place_agent(estante, pos)
                posiciones_disponibles.remove(pos)
                self.schedule.add(estante)

        # Posicionamiento bandas
        banda_entrada = BandaEntrada(101, self)
        self.grid.place_agent(banda_entrada, self.posiciones_bandas[0][1])
        self.schedule.add(banda_entrada)
        banda_salida = BandaSalida(102, self)
        self.grid.place_agent(banda_salida, self.posiciones_bandas[1][1])
        self.schedule.add(banda_salida)

        # Posicionamiento de robots
        for id in range(self.num_agentes):
            robot = RobotDeCarga(id, self)
            self.grid.place_agent(robot, (0, id))
            self.schedule.add(robot)
            # if len(Habitacion.sig_pos_robots) < id+1:
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
            agentes_estante = get_agentes_pos(self, i)
            for agente in agentes_estante:
                if isinstance(agente, Estante) and agente.lleno != True and agente.cant_paquetes == 0:
                    estantes_disponibles.append(agente)
        if len(estantes_disponibles) == 0:
            for i2 in self.posiciones_estantes[tipo]:
                agentes_estante = get_agentes_pos(self, i2)
                for agente2 in agentes_estante:
                    if isinstance(agente2, Estante) and agente2.lleno != True:
                        estantes_disponibles.append(agente2)
        return estantes_disponibles
    
    def get_banda_entrada(self):
        agentes = get_agentes_pos(self, self.posiciones_bandas[0][1])
        for i in agentes:
            if isinstance(i, BandaEntrada):
                return i
    
    def get_banda_salida(self):
        agentes = get_agentes_pos(self, self.posiciones_bandas[1][1])
        for i in agentes:
            if isinstance(i, BandaSalida):
                return i
            
    def step(self):
        z = 0
        print('Running step...')  # For debugging
        print(f'Step: {self.schedule.steps}')  # For debugging
        self.current_step_data['step'] = self.schedule.steps
        self.current_step_data['agents'] = {}
        print('Getting agent data...')
        #print(f'Agents: {self.schedule.agents}')
        for agent in self.schedule.agents:
            if isinstance(agent, RobotDeCarga):
                agent_type = 'Robot'
            elif isinstance(agent, Paquete):  # Replace Paquete with your actual Package class name
                agent_type = 'Package'
                """
                for possible_shelf in self.posiciones_estantes:
                    print(f'POSIBLE ESTANTE: {possible_shelf}')
                    print(f'POSIBLE AGENTE POS: {agent.pos}')
                    if agent.pos in possible_shelf:
                        corresponding_shelf = None
                        for another_agent in self.schedule.agents:
                            if(isinstance(another_agent, Estante) and another_agent.pos in possible_shelf):
                                corresponding_shelf = another_agent
                                break

                        if corresponding_shelf is not None:
                            num_packages = corresponding_shelf.cant_paquetes
                            print(f'ESTANTE {num_packages} paquetes')
                            if num_packages == 0:
                                z = 1
                            elif num_packages == 1:
                                z = 2
                            elif num_packages == 2:
                                z = 3
                            else:
                                z = 3
                            """
            else:
                continue  # Skip this agent, don't add it to current_step_data

            
            self.current_step_data['agents'][agent.unique_id] = {'x': agent.pos[0], 'y': agent.pos[1], 'type': agent_type}
           # self.current_step_data['agents'][agent.unique_id] = {'x': agent.pos[0], 'y': agent.pos[1], 'z': z, 'type': agent_type}

     # Send data to API
        print('Sending data to API...')  # For debugging
        response = requests.post('http://127.0.0.1:5000/api/update', json=self.current_step_data)
        if response.status_code == 200:
            print('Data successfully sent to API')
        else:
            print(f'Failed to send data to API. Status code: {response.status_code}')

       

        self.index_paquete += 1
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
            
        
        self.schedule.step()

        if len(self.pedidos) < 5:
            nuevo_pedido = Pedido(self.index_paquete+1, random.randint(0, 3))
            self.pedidos.append(nuevo_pedido)
    
"""
Modelo Reto END
"""