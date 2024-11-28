A = "A"
B = "B"
C = "C"
D = "D"
E = "E"
F = "F"
G = "G"
H = "H"
I = "I"
J = "J"
K = "K"
L = "L"
N = "N"
O = "O"
P = "P"
Q = "Q"
R = "R"
S = "S"
T = "T"
U = "U"
V = "V"
W = "W"
X = "X"
Y = "Y"
Z = "Z"



class Node:
    def __init__(
        self, nombre="Sin nombre", valor=None, dadN=None, childL=None, childD=None, root=False
    ):
        self.validation(dadN)
        self.validation(childL)
        self.validation(childD)
        self.nombre = nombre
        self.valor = valor
        self.node_dad = dadN
        self.node_child_left = childL
        self.node_child_right = childD
        self.am_i_root = root

    def validation(self, node):
        if node is not None and not isinstance(node, Node):
            raise TypeError("El nodo debe ser una instancia de Node o None")

    def add_left_child(self, child_node):
        """Añadir hijo izquierdo"""
        self.validation(child_node)
        child_node.add_dad(self)
        self.node_child_left = child_node

    def add_right_child(self, child_node):
        """Añadir hijo derecho"""
        self.validation(child_node)
        child_node.add_dad(self)
        self.node_child_right = child_node

    def add_dad(self, dad_node):
        self.validation(dad_node)
        if not self.node_dad:
            self.node_dad = dad_node

    def get_node_info(self):
        dad = self.node_dad
        childL = self.node_child_left
        childD = self.node_child_right
        return dad, childL, childD
    
    def __str__(self):
        text = f"""
        Nombre: {self.nombre}
        Valor: {self.valor}
        Root: {self.am_i_root}
        Dad: {self.node_dad.nombre if self.node_dad else None}
        Child Left: {self.node_child_left.nombre if self.node_child_left else None}
        Child Right: {self.node_child_right.nombre if self.node_child_right else None}
        """
        return text


class Arbol:
    def __init__(self, arbol_data):
        self.arbol_data = arbol_data
        self.lista_nodos = self.creador_nodos(len(arbol_data.items()))
        self.asignar_nombres()
        self.asignar_hijos()

    def creador_nodos(self, numero_nodos):
        return [Node() for _ in range(numero_nodos)]

    def asignar_nombres(self):
        for i, (nodo, conexiones_nodo) in enumerate(self.arbol_data.items()):
            node = self.lista_nodos[i]
            node.nombre = nodo

    def find_node(self, nombre):
        for nodo in self.lista_nodos:
            if nodo.nombre == nombre:
                return nodo
        return None

    def asignar_hijos(self):
        for i, (nodo, conexiones_nodo) in enumerate(self.arbol_data.items()):
            node = self.lista_nodos[i]
            nodo_hijo_izq = self.find_node(conexiones_nodo[0])
            nodo_hijo_der = self.find_node(conexiones_nodo[1])
            if i == 0:
                node.am_i_root = True
            if nodo_hijo_izq:
                node.add_left_child(nodo_hijo_izq)
            if nodo_hijo_der:
                node.add_right_child(nodo_hijo_der)

    def imprimir_nodos(self):
        root = next((nodo for nodo in self.lista_nodos if nodo.am_i_root), None)
        if root:
            self._imprimir_nodo(root, "", True)

    def _imprimir_nodo(self, nodo, prefix, is_tail):
        print(prefix + ("└── " if is_tail else "├── ") + str(nodo.nombre))
        children = [nodo.node_child_left, nodo.node_child_right]
        children = [child for child in children if child is not None]
        for i, child in enumerate(children):
            self._imprimir_nodo(child, prefix + ("    " if is_tail else "│   "), i == len(children) - 1)

    # Métodos de recorridos
    def preorder(self, node):
        if node:
            print(node.nombre, end=" ")
            self.preorder(node.node_child_left)
            self.preorder(node.node_child_right)

    def inorder(self, node):
        if node:
            self.inorder(node.node_child_left)
            print(node.nombre, end=" ")
            self.inorder(node.node_child_right)

    def postorder(self, node):
        if node:
            self.postorder(node.node_child_left)
            self.postorder(node.node_child_right)
            print(node.nombre, end=" ")








import numpy as np
from queue import PriorityQueue


# Nodo específico para Grafo
class NodeGrafo:
    def __init__(self, nombre="Sin nombre", valor=None):
        self.nombre = nombre
        self.valor = valor
        self.vecinos = {}

    def __str__(self):
        text = f"""
        Nombre: {self.nombre}
        Valor: {self.valor}
        Vecinos: {', '.join(f'{vecino.nombre} (peso: {peso})' for vecino, peso in self.vecinos.items())}
        """
        return text


# Clase Grafo usando NodeGrafo
class Grafo:
    def __init__(self, grafo_data=None, dirigido=False):
        self.dirigido = dirigido
        self.lista_nodos = []
        if grafo_data:
            self.crear_nodos(len(grafo_data.items()))
            self.asignar_nombres(grafo_data)
            self.asignar_aristas(grafo_data)

    def crear_nodos(self, numero_nodos):
        self.lista_nodos = [NodeGrafo() for _ in range(numero_nodos)]

    def asignar_nombres(self, grafo_data):
        for i, (nodo, _) in enumerate(grafo_data.items()):
            self.lista_nodos[i].nombre = nodo

    def find_node(self, nombre):
        for nodo in self.lista_nodos:
            if nodo.nombre == nombre:
                return nodo
        return None

    def asignar_aristas(self, grafo_data):
        for nombre_nodo, conexiones in grafo_data.items():
            nodo_origen = self.find_node(nombre_nodo)
            for nombre_vecino, peso in conexiones:
                nodo_vecino = self.find_node(nombre_vecino)
                if nodo_vecino:
                    nodo_origen.vecinos[nodo_vecino] = peso
                    if not self.dirigido:
                        nodo_vecino.vecinos[nodo_origen] = peso

    def imprimir_grafo(self):
        for nodo in self.lista_nodos:
            print(nodo)


    # Recorrido DFS
    def dfs(self, inicio):
        inicio_node = self.find_node(inicio)
        visitados = set()

        def _dfs(nodo):
            if nodo not in visitados:
                print(nodo.nombre, end=" ")
                visitados.add(nodo)
                for vecino in nodo.vecinos:
                    _dfs(vecino)

        _dfs(inicio_node)

    # Recorrido BFS
    def bfs(self, inicio):
        inicio_node = self.find_node(inicio)
        visitados = set()
        cola = [inicio_node]

        while cola:
            nodo = cola.pop(0)
            if nodo not in visitados:
                print(nodo.nombre, end=" ")
                visitados.add(nodo)
                cola.extend(vecino for vecino in nodo.vecinos if vecino not in visitados)

    # Algoritmo de Dijkstra
    def dijkstra(self, inicio):
        inicio_node = self.find_node(inicio)
        distancias = {nodo: float("inf") for nodo in self.lista_nodos}
        distancias[inicio_node] = 0
        pq = PriorityQueue()
        pq.put((0, inicio_node))

        while not pq.empty():
            distancia_actual, nodo_actual = pq.get()

            if distancia_actual > distancias[nodo_actual]:
                continue

            for vecino, peso in nodo_actual.vecinos.items():
                distancia = distancia_actual + peso
                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    pq.put((distancia, vecino))

        return {nodo.nombre: dist for nodo, dist in distancias.items()}

    # Algoritmo de Kruskal
    def kruskal(self):
        aristas = [
            (peso, nodo.nombre, vecino.nombre)
            for nodo in self.lista_nodos
            for vecino, peso in nodo.vecinos.items()
            if self.dirigido or nodo.nombre < vecino.nombre
        ]
        aristas.sort()
        parent = {nodo.nombre: nodo.nombre for nodo in self.lista_nodos}
        rank = {nodo.nombre: 0 for nodo in self.lista_nodos}

        def find(nodo):
            if parent[nodo] != nodo:
                parent[nodo] = find(parent[nodo])
            return parent[nodo]

        def union(nodo1, nodo2):
            root1 = find(nodo1)
            root2 = find(nodo2)
            if root1 != root2:
                if rank[root1] > rank[root2]:
                    parent[root2] = root1
                elif rank[root1] < rank[root2]:
                    parent[root1] = root2
                else:
                    parent[root2] = root1
                    rank[root1] += 1

        mst = []
        for peso, nodo1, nodo2 in aristas:
            if find(nodo1) != find(nodo2):
                union(nodo1, nodo2)
                mst.append((nodo1, nodo2, peso))

        return mst

    # Algoritmo de Prim
    def prim(self, inicio):
        inicio_node = self.find_node(inicio)
        visitados = set([inicio_node])
        aristas = [
            (peso, inicio_node.nombre, vecino.nombre)
            for vecino, peso in inicio_node.vecinos.items()
        ]
        arbol = []

        while aristas:
            aristas.sort()
            peso, nodo1, nodo2 = aristas.pop(0)
            nodo2_obj = self.find_node(nodo2)
            if nodo2_obj not in visitados:
                visitados.add(nodo2_obj)
                arbol.append((nodo1, nodo2, peso))

                for vecino, peso in nodo2_obj.vecinos.items():
                    if vecino not in visitados:
                        aristas.append((peso, nodo2_obj.nombre, vecino.nombre))

        return arbol


# Ejemplo de uso
grafo_data = {
    A: [(B, 2), (C, 6)],
    B: [(A, 2), (C, 3), (D, 8)],
    C: [(A, 6), (B, 3), (E, 7)],
    D: [(B, 8), (E, 9)],
    E: [(C, 7), (D, 9)],
}

grafo = Grafo(grafo_data)
print("Grafo:")
grafo.imprimir_grafo()

print("\nDFS desde A:")
grafo.dfs("A")

print("\n\nBFS desde A:")
grafo.bfs("A")

print("\n\nDijkstra desde A:")
print(grafo.dijkstra("A"))

print("\nKruskal:")
print(grafo.kruskal())

print("\nPrim desde A:")
print(grafo.prim("A"))



# Arbol de ejemplo
ARBOL = {
    A: [B, C],
    B: [D, E],
    D: [None, None],
    E: [None, None],
    C: [None, F],
    F: [H, G],
    G: [None, None],

}

# Uso de la clase Arbol
arbol = Arbol(ARBOL)
print("Árbol:")
arbol.imprimir_nodos()

print("\nPreorden:")
arbol.preorder(arbol.lista_nodos[0])

print("\n\nInorden:")
arbol.inorder(arbol.lista_nodos[0])

print("\n\nPostorden:")
arbol.postorder(arbol.lista_nodos[0])

