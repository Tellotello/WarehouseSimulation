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
def registrar_log(message):
    """
    Funcion para debug
    """
    with open("log.txt", 'a') as log:
        log.write(message)
        log.close()
    # pass



def distancia_entre_puntos(p1, p2):
    """
    Calcula la distancia entre 2 puntos.
    """
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

def get_celdas_vecinas(pos, include_center = False):
    celdas_vecinas = [
        (pos[0]+1, pos[1]),
        (pos[0], pos[1]+1),
        (pos[0]-1, pos[1]),
        (pos[0], pos[1]-1)
    ]
    celdas_vecinas_limpias = []
    for i in celdas_vecinas:
        if i[0] < 15 and i[1] < 15 and i[0] > -1 and i[1] > -1:
            celdas_vecinas_limpias.append(i)
    if include_center:
        celdas_vecinas_limpias.append(pos)
    return celdas_vecinas_limpias


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

class ContratoActividad():
    def __init__(self, robot, actividad):
        self.robot = robot
        self.actividad = actividad



    
M = N = 15

class Estante(Agent):
    def __init__(self, unique_id, model, tipo):
        super().__init__(unique_id, model)
        self.tipo = tipo 
        self.lleno = False
        self.cant_paquetes = 0
    
    def step(self):
        if self.cant_paquetes > 1:
            self.lleno = True
        else:
            self.lleno = False
        agentes = get_agentes_pos(self.model, self.pos)
        cuenta = 0
        for i in agentes:
            if isinstance(i, Paquete):
                cuenta += 1
        if cuenta > 1:
            self.cant_paquetes = cuenta
            self.lleno = True
    
class BandaSalida(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # Se registran los paquetes en forma de (self, id_paquete, id_robot, tipo_pedido=None)
        self.contratos_pedidos = []
    


    def hay_pedido(self):
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
        if cuenta > 3:
            registrar_log(f'\nHay paquete de tipo {tipo} disponible')
            return True
        else:
            registrar_log(f'\nNo hay paquete de tipo {tipo} disponible')
            return False



    def contratar_robot_entregar(self, tipo, id_pedido):
        """
        Contrata robot para entregar, primero al mas cercano que no este ocupado,
        si no hay le da la tarea al mas cercano que tenga menos de 3 actividades.
        """
        pos_robots = []
        for i in self.model.robots:
            if  i.ocupado == False:
                pos_robots.append(i.pos)
        if len(pos_robots) == 0:
            for i in self.model.robots:
                if len(i.actividades) < 3:
                    pos_robots.append(i.pos)
        if pos_robots:
            registrar_log(f'\n Si hay robots disponibles para pedido {id_pedido}')
        
            
            pos_min_distancia = get_pos_cercana(self.pos, pos_robots)

            robot_cercano = get_agentes_pos(self.model, pos_min_distancia)
            for i in robot_cercano:
                if isinstance(i, RobotDeCarga):
                    entregar_act = Actividad(4, self.pos, tipo, id_pedido=id_pedido)
                    i.actividades.append(entregar_act)
                    return i.unique_id
        else:
            registrar_log(f'\nNo hay robots disponibles para pedido {id_pedido}')
            return -1
            

    
    def pedido_entregado(self, paquete_id, id_pedido):
            for i in range(len(self.contratos_pedidos)):
                if self.contratos_pedidos[i].id_pedido == id_pedido:
                    self.contratos_pedidos.pop(i)
                    break
                #Remover de pedidos en modelo
                for i, p in enumerate(self.model.pedidos):
                    if p.id == id_pedido:
                        self.model.pedidos.pop(i)

                            

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
                    self.paquetes.append(nuevo_contrato)
                    
    
    def paquete_registrado(self, id):
        for i in self.paquetes:
            if i.id_paquete == id:
                return True
        return False

    
    def contratar_robot_recoger(self):
        """
        Contrata robot para entregar, primero al mas cercano que no este ocupado,
        si no hay le da la tarea al mas cercano que tenga menos de 3 actividades.
        """
        pos_robots = []
        for i in self.model.robots:
            if i.ocupado == False:
                pos_robots.append(i.pos)

        if len(pos_robots) == 0:
            for i in self.model.robots:
                if len(i.actividades) < 3:
                    pos_robots.append(i.pos)
        if pos_robots:
            
            pos_min_distancia = get_pos_cercana(self.pos, pos_robots)

            robot_cercano = get_agentes_pos(self.model, pos_min_distancia)
            for i in robot_cercano:
                if isinstance(i, RobotDeCarga):
                    self.paquetes[-1].id_robot = i.unique_id # robot contratado
                    nueva_actividad = Actividad(1, self.pos)
                    i.actividades.append(nueva_actividad)
                    break
            

    
    def paquete_recogido(self, paquete_id):

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
    
    def step(self):
        agentes_estacion_carga = get_agentes_pos(self.model, self.pos)
        for i in agentes_estacion_carga:
            if isinstance(i, RobotDeCarga):
                if i.carga+25 > 100:
                    i.carga = 100
                else:
                    i.carga += 25
                



class Paquete(Agent):
    def __init__(self, unique_id, model, tipo):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.tipo = tipo
        self.disponible = True



    

class RobotDeCarga(Agent):
    actividades_disponibles = []
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.recorrido = []
        self.ocupado = False
        self.id_paquete_recoger = None
        self.carga = 100

        #Test
        self.instancia_moviendo_paquete = None # Instancia de paquete moviendo

        # Sistema de actividades
        # 1. Recoger paquete de banda de entrada
        # 2. Almacenar paquete en estante
        # 3. Recoger paquete de estante
        # 4. Entregar paquete en banda de salida
        # 5. Irse a cargar
        self.actividades = []

    

    def lista_celdas_vecinas_disponibles(self, pos, robot_obstaculo):
        """
        Regresa lista de celdas disponibles.
        """
        # lista_de_celdas_vecinas = self.model.grid.get_neighborhood(
        # pos, 
        # moore=False,
        # include_center=False)
        lista_de_celdas_vecinas = get_celdas_vecinas(pos)

        lista_de_vecinos_agentes = self.model.grid.get_neighbors(
        pos, moore=False, include_center=False)

        # Quitar la celdas vecinas que no esten disponibles
        for i in lista_de_vecinos_agentes:
            if robot_obstaculo == False:
                if isinstance(i, Estante) == True or isinstance(i, BandaEntrada) == True or isinstance(i, BandaSalida) == True:
                    if i.pos in lista_de_celdas_vecinas:
                        index_pos_agente = lista_de_celdas_vecinas.index(i.pos)
                        lista_de_celdas_vecinas.pop(index_pos_agente)
            else:
                if isinstance(i, Estante) == True or isinstance(i, BandaEntrada) == True or isinstance(i, BandaSalida) == True or isinstance(i, RobotDeCarga):
                    if i.pos in lista_de_celdas_vecinas:
                        index_pos_agente = lista_de_celdas_vecinas.index(i.pos)
                        lista_de_celdas_vecinas.pop(index_pos_agente)
        # registrar_log(f'\nVecinos de {pos}: {lista_de_celdas_vecinas} con robot_obtaculo de: {robot_obstaculo}')
        return lista_de_celdas_vecinas

    def get_estante_entregar(self, tipo):
        """
        Regresa posicion de estante
        disponible mas cercano de un tipo.
        """
        estantes = self.model.get_estantes(tipo)
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
        else: 
            registrar_log('\nNo se encontro estante')
            return None
    

    def get_paquete_cercano(self, tipo):
        """
        Regresa posicion de paquete disponible 
        mas cercano de un tipo.
        """

        pos_estantes = self.model.posiciones_estantes[tipo]

        paquetes_cercanos = []
        for i in pos_estantes:
            agentes_estante = get_agentes_pos(self.model, i)
            for n in agentes_estante:
                if isinstance(n, Paquete) and n.disponible:
                    paquetes_cercanos.append(n)
        pos_paquetes_cercanos = [q.pos for q in paquetes_cercanos]
        registrar_log(f'\n Pos paquetes tipo {tipo}: {[m.pos for m in paquetes_cercanos]}')

        pos_paquete_cercano = get_pos_cercana(self.pos, pos_paquetes_cercanos)
        index_paquete_cercano = pos_paquetes_cercanos.index(pos_paquete_cercano)
        paquete_cercano = paquetes_cercanos[index_paquete_cercano]
        id_paquete = paquete_cercano.unique_id
        paquete_cercano.disponible = False

        agentes_pos = get_agentes_pos(self.model, pos_paquete_cercano)
        for p in agentes_pos:
            if isinstance(p, Estante):
                p.cant_paquetes -= 1
        
        return id_paquete, pos_paquete_cercano


    def recoger_paquete_banda(self, instancia_paquete):
        registrar_log(f"\nEl robot {self.unique_id} entro a recoger_paquete_banda instancia parametro {type(instancia_paquete)}, instancia self {type(self.instancia_moviendo_paquete)}")
        self.instancia_moviendo_paquete = instancia_paquete
        estante_cercano = self.get_estante_entregar(instancia_paquete.tipo)
        actividad_nueva = Actividad(2, estante_cercano)
        self.actividades.append(actividad_nueva)
        self.actividades.pop(0)
        instancia_paquete.disponible = False
        self.ocupado = True
        registrar_log(f"\nEl robot {self.unique_id} final de recoger_paquete_banda instancia parametro {type(instancia_paquete)}, instancia self {type(self.instancia_moviendo_paquete)}")
    

    def recoger_paquete_estante(self, instancia_paquete, instancia_estante):
        self.instancia_moviendo_paquete = instancia_paquete
        if self.actividades[0].tipo_actividad == 3:
            self.actividades.pop(0)
        instancia_estante.cant_paquetes -= 1
        instancia_paquete.disponible = False
        self.ocupado = True
        self.id_paquete_recoger = None


    def mover_paquete(self, instancia_paquete):
        instancia_paquete.model.grid.move_agent(instancia_paquete, self.sig_pos)

    def entregar_paquete_estante(self, instancia_paquete, pos_estante):
        registrar_log(f"\nEl robot {self.unique_id} entro a entregar_paquete_estante instancia parametro {type(instancia_paquete)}, instancia self {type(self.instancia_moviendo_paquete)}")
        if instancia_paquete:
            instancia_paquete.model.grid.move_agent(instancia_paquete, pos_estante)
            instancia_paquete.disponible = True
            self.model.get_banda_entrada().paquete_recogido(instancia_paquete.unique_id)
        self.instancia_moviendo_paquete = None
        self.actividades.pop(0)
        self.ocupado = False
        # agentes_estante = get_agentes_pos(self.model, pos_estante)
        # for i in agentes_estante:
        #     if isinstance(i, Estante):
        #         i.cant_paquetes += 1
        #         break
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
        # if len(self.actividades) == 0:
        #     self.irse_reposo()

    def ofertar_actividad(self):
        """
        Buscar en reversa la primer actividad 1
        y ofertarla a otros robots.
        """
        for i in range(len(self.actividades)-1, -1, -1):
            if self.actividades[i].tipo_actividad == 1:
                contrato_actividad = ContratoActividad(None, self.actividades[0])
                self.actividades_disponibles.append(contrato_actividad)
                self.actividades.pop(i)
                break

    def irse_a_cargar(self):
        pos_cargadores_disponibles = self.model.get_estaciones_disponibles()
        registrar_log(f'\n2.2 Se entro a irse a cargar de pila')
        registrar_log(f'\npos_cargadores_disponibles: {pos_cargadores_disponibles}')
        pos_cargador_cercano = get_pos_cercana(self.pos, pos_cargadores_disponibles)
        if pos_cargador_cercano != self.pos:
            registrar_log(f'\nSe borro recorrido de robot {self.unique_id}')
            self.recorrido = []
            if self.actividades and self.actividades[0].tipo_actividad == 1:
                self.ofertar_actividad()
            actividad_carga = Actividad(5, pos_cargador_cercano)
            self.actividades.insert(0, actividad_carga)
            agentes_pos = get_agentes_pos(self.model, pos_cargador_cercano)
            for i in agentes_pos:
                if isinstance(i, EstacionDeCarga):
                    i.ocupada = True
    
    def irse_reposo(self):
        if len(self.actividades) == 0 or self.actividades[0].tipo_actividad == 4:
            act_reposar = Actividad(6, (5+self.unique_id, 7))
            self.actividades.append(act_reposar)

    def hay_robot(self, pos):
        agentes_pos = get_agentes_pos(self.model, pos)
        for i in agentes_pos:
            registrar_log(f'\nTipo agente en {pos}: {type(i)}')
            if isinstance(i, RobotDeCarga):
                return True
        return False
 
    # A Star Algo
    # Si el tipo es True, no se cuentan los robots como obstaculos
    # Si el tipo es False, si se cuentan los robots como obstaculos
    def a_star_path(self, pos_inicial, pos_final, robot_obstaculo):
        
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
            
            def get_nodo(self, pos):
                for i in self.queue:
                    if i.coord == pos:
                        return i
                return None
            
            def pos_in_open(self, coord):
                for node in self.queue:
                    if node.coord == coord:
                        return node
                return None
            

        def pos_in_closed(coord, closed):
            for node in closed:
                if node.coord == coord:
                    return node
            return None
        
        nodo_actual = Node(pos_inicial, 0, 0, None)
        open = Queue()
        open.push(nodo_actual)
        pos_encontrada = False
        closed = list()

        pos_visitadas = []
        while pos_encontrada != True:
            # lista_de_celdas_vecinas = self.model.grid.get_neighborhood(
            # nodo_actual.coord, 
            # moore=False,
            # include_center=False)
            lista_de_celdas_vecinas = get_celdas_vecinas(nodo_actual.coord)


            # if pos_final in lista_de_celdas_vecinas or distancia_entre_puntos(nodo_actual.coord, pos_final) < 2:
            # if pos_final in lista_de_celdas_vecinas or distancia_entre_puntos(nodo_actual.coord, pos_final) <= 1:
            if pos_final in lista_de_celdas_vecinas:
                pos_encontrada = True
                break

            open.pop()
            lista_vecinos = self.lista_celdas_vecinas_disponibles(nodo_actual.coord, robot_obstaculo)

            # registrar_log(f'\nlista_vecinos_normal: {lista_vecinos}')
            for i in lista_vecinos:

                # if i not in pos_visitadas:
                #     g_cost = nodo_actual.g_cost+0.5
                #     h_cost = distancia_entre_puntos(i, pos_final)
                #     vertice = Node(i, g_cost, h_cost, nodo_actual)
                #     open.push(vertice)
                #     pos_visitadas.append(i)


                g_cost = nodo_actual.g_cost+0.5
                h_cost = distancia_entre_puntos(i, pos_final)
                vertice = Node(i, g_cost, h_cost, nodo_actual)

                if i in pos_visitadas:
                    nodo_pos_closed = pos_in_closed(i, closed)
                    nodo_pos_open = open.pos_in_open(i)
                    # registrar_log(f'\nnodo_Pos_closed: {nodo_pos_closed}, nodo_Pos_open: {nodo_pos_open}')
                    if nodo_pos_closed:
                        if nodo_pos_closed.f_cost > vertice.f_cost:
                            nodo_pos_closed.g_cost = vertice.g_cost
                            nodo_pos_closed.h_cost = vertice.h_cost
                            nodo_pos_closed.viene_de = vertice.viene_de
                    elif nodo_pos_open:
                        if nodo_pos_open.f_cost > vertice.f_cost:
                            open.queue.remove(nodo_pos_open)
                            nodo_pos_open.g_cost = vertice.g_cost
                            nodo_pos_open.h_cost = vertice.h_cost
                            nodo_pos_open.viene_de = vertice.viene_de
                            open.push(nodo_pos_open)
                else:
                    open.push(vertice)
                    pos_visitadas.append(i)

            if open.get_size() == 0:
                return []
            else:
                # for i in open.queue:
                    # registrar_log(f'\nPos: {i.coord}, f_cost: {i.f_cost}')
                registrar_log(f'\n{nodo_actual.coord}')
                nodo_actual = open.get_head()
                closed.append(nodo_actual)


        camino = []
        while nodo_actual.coord != pos_inicial:
            camino.insert(0, nodo_actual.coord)
            nodo_actual = nodo_actual.viene_de
        registrar_log(f'\nCamino: {camino}')
        return camino
            
    def calcular_nuevo_camino(self, actividad_actual):
        """
        Calcula nuevo camino en base a la pos_final de la actividad actual.
        Si no hay camino posible mueve al robot a una celda vecina y espera 
        a que el robot vecino pase.
        """
        self.recorrido = []
        self.recorrido += self.a_star_path(self.pos, actividad_actual.pos_final, True)
        if len(self.recorrido) > 0:
            self.sig_pos = self.recorrido[0]
            registrar_log(f'\nSe calculo nuevo camino para robot {self.unique_id}: {self.recorrido}')
            self.recorrido.pop(0)
        else:
            celdas_vecinas = self.lista_celdas_vecinas_disponibles(self.pos, True)
            if celdas_vecinas:
                if celdas_vecinas[0] in self.model.sig_pos_robots:
                    self.recorrido.append(celdas_vecinas[1])
                else:
                    self.recorrido.append(celdas_vecinas[0])
            else:
                self.recorrido.append(self.pos)

            registrar_log(f'\nSNo se encontro nuevo camino para robot {self.unique_id}')
            
            # self.quedarse_en_pos()
    
    def quedarse_en_pos(self):
        """
        sig_pos = self.pos
        """
        self.sig_pos = self.pos
    
    def get_sig_pos_robots(self):
        sig_pos_robots = self.model.sig_pos_robots.copy()
        sig_pos_robots.pop(self.unique_id)
        return sig_pos_robots
        
    def step(self):
        registrar_log(f'\nAcitivdades disponibles')
        for i in self.actividades_disponibles:
            registrar_log(f'\nTipo: {i.actividad.tipo_actividad}, robot: {type(i.robot)}')
        registrar_log(f'\nCeldas vecinas de {self.pos}: {self.lista_celdas_vecinas_disponibles(self.pos, False)}')

        registrar_log(f'\n El robot {self.unique_id} se encuentra en {self.pos}, carga de: {self.carga}, ocupado de: {self.ocupado}, con recorrido de {self.recorrido}, instancia_paquete: {type(self.instancia_moviendo_paquete)} y {len(self.actividades)} actividades')
        registrar_log(f'\nACTIVIDADES Robot {self.unique_id}')
        for a in self.actividades:
            registrar_log(f'\n id_act: {a.tipo_actividad}, pos_final: {a.pos_final}, tipo_pedido: {a.tipo_pedido}, id_pedido: {a.id_pedido}')
        # No Estan ocupados
        # no tienen recorrido
        # lista_de_vecinos = self.model.grid.get_neighborhood(
        #     self.pos, 
        #     moore=False,
        #     include_center=True)
        lista_de_vecinos = get_celdas_vecinas(self.pos, include_center=True)

        if len(self.actividades) > 0:
            if self.actividades[0].tipo_actividad == 6:
                self.ocupado = False
            else:
                self.ocupado = True
            registrar_log(f'\n2. Si hay actividades')

            # Estoy haciendo una act 6 y tengo actividades
            if len(self.actividades) > 1 and self.actividades[0].tipo_actividad == 6:
                if self.recorrido and self.recorrido[-1] in get_celdas_vecinas(self.actividades[0].pos_final):
                    self.recorrido = []
                self.actividades.pop(0)
                actividad_actual = self.actividades[0]
            
            if len(self.actividades) > 1:
                for i in self.actividades:
                    self.ofertar_actividad()

            actividad_actual = self.actividades[0]

            # Intentar hacer la funcion de irse a cargar dinamica
            # Irse a cargar
            if self.carga < 60 and self.instancia_moviendo_paquete == None and actividad_actual.tipo_actividad != 5:
                self.irse_a_cargar()

            elif actividad_actual.tipo_actividad == 4 and self.instancia_moviendo_paquete == None:

                registrar_log(f'\n2.3 Se entro a act 4')
                self.recorrido = []
                registrar_log(f"\nSi hay paquete disponible de tipo {actividad_actual.tipo_pedido}")
                id_paquete, pos_paquete = self.get_paquete_cercano(actividad_actual.tipo_pedido)
                registrar_log("\n=======Entre a la condicion rara")
                registrar_log(f'\nid_paquete: {id_paquete}, pos_paquete: {pos_paquete}, tipo: {actividad_actual.tipo_pedido}, pos_actual: {self.pos}')
                self.id_paquete_recoger = id_paquete
                actividad_recoger = Actividad(3, pos_paquete, actividad_actual.tipo_pedido)
                self.ocupado = True
                self.actividades.insert(0, actividad_recoger)

            elif actividad_actual.pos_final in lista_de_vecinos:
                registrar_log(f'\n3. Se encontro una pos final')
                # Hacer el if-elif largo con los pasos para cada actividad

                # Recoger paquete de BandaEntrada
                if actividad_actual.tipo_actividad == 1:
                        registrar_log(f'\n3.1 ACT 1')
                        agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                        if len(agentes) > 0:
                            for agente in agentes:
                                if isinstance(agente, Paquete) and agente.disponible == True:
                                    registrar_log(f'\ntypo_agente_2: {type(agente) }')
                                    self.recoger_paquete_banda(agente)
                                    break
                # Almacenar paquete en estante
                elif actividad_actual.tipo_actividad == 2:
                    registrar_log(f'\n3.2 ACT 2')
                    agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                    if len(agentes) > 0:
                        for agente in agentes:
                            if isinstance(agente, Estante):
                                registrar_log(f'\ntipo_paquete: {type(self.instancia_moviendo_paquete)}')
                                self.entregar_paquete_estante(self.instancia_moviendo_paquete, actividad_actual.pos_final)
                                self.irse_reposo()
                                break
                # Recoger paquete de estante       
                elif actividad_actual.tipo_actividad == 3:
                    registrar_log(f'\n3.3 ACT 3')
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
                    # self.irse_reposo()

                # Entregar paquete en BandaSalida 
                elif actividad_actual.tipo_actividad == 4 and self.instancia_moviendo_paquete:
                    registrar_log(f'\n3.4 ACT 4')
                    agentes = get_agentes_pos(self.model, actividad_actual.pos_final)
                    if len(agentes) > 0:
                        for agente in agentes:
                            if isinstance(agente, BandaSalida):
                                self.entregar_paquete_banda(self.instancia_moviendo_paquete, agente.pos, id_pedido=actividad_actual.id_pedido)
                                break
                    self.irse_reposo()
                elif actividad_actual.tipo_actividad == 5:
                    registrar_log(f'\n3.5 ACT 5')
                    if self.pos != actividad_actual.pos_final:
                        self.recorrido.insert(0, actividad_actual.pos_final)
                    elif self.carga == 100:
                        registrar_log(f'\n2.1 Se entro a act 5')
                        agentes_estacion_carga = get_agentes_pos(self.model, actividad_actual.pos_final)
                        for i in agentes_estacion_carga:
                            if isinstance(i, EstacionDeCarga):
                                i.ocupada = False
                        self.actividades.pop(0)
                        self.irse_reposo()
                elif actividad_actual.tipo_actividad == 6:
                    self.actividades.pop(0)
            
            if len(self.recorrido) == 0:
                registrar_log(f'\nSe agrego a recorrido con act actual de tipo: {actividad_actual.tipo_actividad}')
                registrar_log(f'\nCamino de {self.pos} a {actividad_actual.pos_final}')
                registrar_log(f'\nAntes recorrido era {self.recorrido}')
                recorrido_actividad = self.a_star_path(self.pos, actividad_actual.pos_final, False)
                registrar_log(f'\nSe calculo el camino {recorrido_actividad}')
                self.recorrido += recorrido_actividad
                registrar_log(f'\nAhora recorrido es {self.recorrido}')               

        # Si no tengo actividades 
        else:
            self.ocupado = False
            if self.carga < 60 and self.instancia_moviendo_paquete == None:
                    self.irse_a_cargar()
            elif self.actividades_disponibles:
                for i, contrato in enumerate(self.actividades_disponibles):
                    if contrato.robot == None:
                        self.actividades.append(contrato.actividad)
                        self.actividades_disponibles.pop(i)
            



        if self.carga == 0 or len(self.recorrido) == 0:
                self.sig_pos = self.pos
        else:
            registrar_log(f'\nRecorrido[0] robot {self.unique_id}: {self.recorrido[0]}, con recorrido: {self.recorrido}, sig_pos_robots: {self.get_sig_pos_robots()}')
            # Si un robot se cruza en su camino
            # if self.recorrido[0] in self.get_sig_pos_robots() or self.hay_robot(self.recorrido[0]) == True and self.carga != 100:
            
            if (self.recorrido[0] in self.get_sig_pos_robots() or self.hay_robot(self.recorrido[0])) and self.carga != 100:
                
                # Obtener instancia del robot en tu siguiente posicion
                robot_2 = None
                # agentes = self.model.grid.get_cell_list_contents([self.recorrido[0]])

                agentes = get_agentes_pos(self.model, self.recorrido[0])
                for agente in agentes:
                    if isinstance(agente, RobotDeCarga):
                        # if len(agente.recorrido) == 0 and agente.recorrido[0] == self.recorrido[0]:
                        robot_2 = agente
                        break
                # Si el robot no esta en tu siguiente posicion pero su sig_pos es tu sig_pos
                if robot_2 == None:
                    for id, sig_pos in enumerate(self.model.sig_pos_robots):
                        if id != self.unique_id and sig_pos == self.recorrido[0]:
                            robot_2 = self.model.robots[id]
                
                # Si hay un robot en tu siguiente posicion
                if len(self.actividades) > 1 and ((robot_2.actividades and robot_2.actividades[0].tipo_actividad == 4) or len(robot_2.actividades) == 0):
                    self.ofertar_actividad()
                    if len(robot_2.actividades) == 0 or (robot_2.actividades and robot_2.actividades[0].tipo_actividad == 4):
                        act_reposar = Actividad(6, (5+robot_2.unique_id, 7))
                        robot_2.actividades.insert(0, act_reposar)
                    self.quedarse_en_pos()



                #Test Negociacion
                # agentes_vecinos = self.model.grid.get_neighbors(
                #     self.pos, 
                #     moore=True, 
                #     include_center=False
                #     )
                # robot_2 = get_agente_pos(self.model, RobotDeCarga, self.recorrido[0])





                        # elif len(agente.recorrido) > 0:
                        #     if(agente.pos == self.recorrido[0] or agente.recorrido[0] == self.pos or self.recorrido[0] == agente.recorrido[0]):
                        #         robot_2 = agente
                        #         break
                # Si el otro robot no tiene actividades y tu si
                elif len(self.actividades) > 0 and len(robot_2.actividades) > 0:
                    act_actual = self.actividades[0]
                    act_actual_robot_2 = robot_2.actividades[0]
                    if act_actual.tipo_actividad < act_actual_robot_2.tipo_actividad:
                        self.calcular_nuevo_camino(act_actual)
                    elif act_actual.tipo_actividad > act_actual_robot_2.tipo_actividad:
                        self.quedarse_en_pos()
                    elif act_actual.tipo_actividad == act_actual_robot_2.tipo_actividad:
                        if self.unique_id > robot_2.unique_id:
                            self.calcular_nuevo_camino(act_actual)
                        else:
                            self.quedarse_en_pos()
                # elif len(robot_2.actividades) == 0:
                #     if self.actividades:
                #         self.calcular_nuevo_camino(self.actividades[0])
                #     else:
                #         self.sig_pos = self.pos

            # Moverse a recorrido[0]
            else:
                self.sig_pos = self.recorrido[0]
                self.recorrido.pop(0)

                # Quitar_carga
                if self.instancia_moviendo_paquete:
                    self.carga -= 1
                else:
                    self.carga -= 0.5




    def advance(self):

        if self.recorrido:
            self.model.sig_pos_robots[self.unique_id] = self.recorrido[0]
        self.model.grid.move_agent(self, self.sig_pos)
        if self.instancia_moviendo_paquete:
            self.mover_paquete(self.instancia_moviendo_paquete)
            
                

"""
CLASES RETO END
"""

"""
Modelo Reto START
"""
class Almacen(Model):
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
        self.pedidos = []
        
        self.posiciones_estantes = [
            [(4, 2), (4, 3), (4, 4), (4, 5), (5, 2), (5, 3), (5, 4), (5, 5)],
            [(4, 9), (4, 10), (4, 11), (4, 12), (5, 9), (5, 10), (5, 11), (5, 12)],
            [(9, 2), (9, 3), (9, 4), (9, 5), (10, 2), (10, 3), (10, 4), (10, 5)],
            [(9, 9), (9, 10), (9, 11), (9, 12), (10, 9), (10, 10), (10, 11), (10, 12)]
        ]

        self.posiciones_estaciones_carga = [(2, 0), (12, 0), (2, 14), (12, 14)]

        # Test
        # Hacer una lista de paquetes y cuando se recoja uno que se ponga otro y se tenga que contratar a otro robot
            # Con tipo de entero random range(len(self.posicones_estantes))
        paquete = Paquete(1, self, 2)
        self.index_paquete = 1000

        self.posiciones_bandas = [(True, (0, 7)), (False, (14, 7))]
        

        # Posicionamiento de estantes
        for i in range(len(self.posiciones_estantes)):
            for id, pos in enumerate(self.posiciones_estantes[i]):
                estante = Estante((10000+i)*(id+1), self, i)
                self.grid.place_agent(estante, pos)
                posiciones_disponibles.remove(pos)
                self.schedule.add(estante)

        # Posicionamiento de estaciones de carga
        for i in range(len(self.posiciones_estaciones_carga)):
            estacion_de_carga = EstacionDeCarga((10000-i-1)*(i+1), self)
            self.grid.place_agent(estacion_de_carga, self.posiciones_estaciones_carga[i])
            posiciones_disponibles.remove(self.posiciones_estaciones_carga[i])
            self.schedule.add(estacion_de_carga)

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
            if len(Almacen.robots) < id+1:
                Almacen.sig_pos_robots.append((0, id))
                Almacen.robots.append(robot)
            else:
                Almacen.robots[id] = robot

        self.datacollector = DataCollector(
            model_reporters={
                # "Grid": get_grid, "Cargas": get_cargas,
                #              "CeldasSucias": get_sucias
                "Paquetes": get_cant_paquetes,
            },
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
    
    def get_estaciones_disponibles(self):
        pos_estaciones_disponibles = []
        for i in self.posiciones_estaciones_carga:
            agentes = get_agentes_pos(self, i)
            for a in agentes:
                if isinstance(a, EstacionDeCarga) and a.ocupada == False:
                    pos_estaciones_disponibles.append(i)
        return pos_estaciones_disponibles


    
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
        tipos_pedido = [0, 1, 2, 3]
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
            
        self.datacollector.collect(self)
        self.schedule.step()

        if len(self.pedidos) < 5:
            if self.pedidos:
                tipos_pedido.remove(self.pedidos[-1].tipo)
            nuevo_pedido = Pedido(self.index_paquete+1, random.choice(tipos_pedido))
            self.pedidos.append(nuevo_pedido)
    
"""
Modelo Reto END
"""


def get_cant_paquetes(model: Model):
    contador_paquetes = 0
    for i in model.posiciones_estantes:
        for j in i:
            agentes_pos = get_agentes_pos(model, j)
            for k in agentes_pos:
                if isinstance(k, Paquete):
                    contador_paquetes += 1

    return contador_paquetes
