from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import random

import numpy as np

#no esta en el diagrama de clases
class Celda(Agent):
    def __init__(self, unique_id, model, hay_paquete: bool = False):
        super().__init__(unique_id, model)
        self.estado = hay_paquete

class Paquete(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
                        
class Estante(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.paquetes = []
        
class Pedido(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class RobotMobil(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.available_neighbors = []
        self.recargas = 0
        
    def seleccionar_nueva_pos(self, lista_vecinos):
        self.available_neighbors = []
        for vecino in lista_vecinos:
            if vecino.estado == False:
                self.available_neighbors.append(vecino)
        if len(self.available_neighbors) > 0:
            self.sig_pos = random.choice(self.available_neighbors)
            self.movimientos += 1
        else:
            self.sig_pos = self.pos
        return self.sig_pos
    
  
    def buscar_paquete(lista_vecinos):
       
        
        
    
        
