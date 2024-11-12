class Node:
    def __init__(
        self, nombre="Sin nombre", dadN=None, childL=None, childD=None, root=False
    ):
        self.validation(dadN)
        self.validation(childL)
        self.validation(childD)
        self.nombre = nombre
        self.node_dad = dadN
        self.node_child_left = childL
        self.node_child_right = childD
        self.am_i_root = root

    def validation(self, node):
        if node is not None and not isinstance(node, Node):
            raise TypeError("dadN debe ser una instancia de Node o None")

    def add_left_child(self, child_node):
        """LEEEEEEFTTTTT 👈🏼"""
        
        self.validation(child_node)
        # add dad
        child_node.add_dad(self)
        self.node_child_left = child_node

    def add_right_child(self, child_node):
        """RIGHTTTTTTTTTT 👉🏼"""
        
        self.validation(child_node)
        # add dad
        child_node.add_dad(self)
        self.node_child_right = child_node

    def add_dad(self, dad_node):
        self.validation(dad_node)

        # Tnego papa?
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


# Arbol de ejemplo

ARBOL = {
    "a": ["b", "c"],
    "b": ["d", "e"],
    "d": [None, None],
    "e": [None, None],
    "c": [None, "f"],
    "f": [None, None],
}

# Uso de la clase Arbol
arbol = Arbol(ARBOL)
arbol.imprimir_nodos()

