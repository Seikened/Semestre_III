from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QKeySequence, QGuiApplication, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QHeaderView, QMenu
from PyQt6.QtCore import QTimer, Qt
from modelo.base.productoBase import ProductoBase
from modelo.base.product import Producto
from PyQt6 import uic
import sys

ui = '/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/Desarrollo_Web/appCRUD/ui/crud.ui'

class ProductoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loadUI()
        self.inicializar_tabla()
        # Inicializar el índice de la última fila modificada
        self.ultima_fila_modificada = None
        self.listar_productos()
        # Crear un atajo de teclado para copiar la selección
        self.copy_shortcut = QShortcut(QKeySequence('Ctrl+C'), self)
        self.copy_shortcut.activated.connect(self.copiar_seleccion)

    def loadUI(self):
        self.crudApp = uic.loadUi(ui, self)
        self.setFixedSize(self.width(), self.height()) 

        # Conectar botones a funciones
        self.crudApp.readBtn.clicked.connect(self.listar_productos)
        self.crudApp.createBtn.clicked.connect(self.guardar_producto)
        self.crudApp.deleteBtn.clicked.connect(self.eliminar_producto)
        self.crudApp.searchBtn.clicked.connect(self.buscar_producto)
        self.crudApp.countBtn.clicked.connect(self.contar_productos)

        # Aplicar estilo CSS
        self.crudApp.table.setStyleSheet("""
            QTableView {
                gridline-color: black;
                background-color: #1e1e1e;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #6c6c6c;
            }
            QTableView::item:selected {
                background-color: #aed581;
            }
        """)
    
    def validar_campos(self, clave, descripcion, existencia, precio, all=True):
        if all:
            if not clave or not descripcion or not existencia or not precio:
                return False
            try:
                int(existencia)
                float(precio)
            except ValueError:
                return False
            return True
        else:
            if  clave or descripcion:
                if clave:
                    return True, clave
                elif descripcion:
                    return True, descripcion
            return False, None
    
    def copiar_seleccion(self):
        # Obtener el índice seleccionado de la tabla
        seleccion = self.crudApp.table.selectionModel().selectedIndexes()

        if seleccion:
            # Crear un diccionario para almacenar filas y columnas
            rows = {}
            for index in seleccion:
                fila = index.row()
                columna = index.column()
                # Añadir la celda al diccionario en la fila correspondiente
                if fila not in rows:
                    rows[fila] = {}
                rows[fila][columna] = self.modelo.item(index.row(), index.column()).text()
            
            # Construir el texto a copiar como filas separadas por tabulaciones y saltos de línea
            texto_a_copiar = "\n".join(
                "\t".join(rows[fila][col] for col in sorted(rows[fila].keys()))
                for fila in sorted(rows.keys())
            )
            
            # Copiar el texto al portapapeles
            QGuiApplication.clipboard().setText(texto_a_copiar)

        else:
            self.mostrar_mensaje("Información", "No hay celdas seleccionadas para copiar.")

    
    def limpiar_campos(self):
        self.crudApp.claveLabel.setText('')
        self.crudApp.descripcionLabel.setText('')
        self.crudApp.existenciaLabel.setText('')
        self.crudApp.precioLabel.setText('')
    
    def mostrar_mensaje(self, titulo, mensaje):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.exec()
    
    # Inicializar la tabla con un modelo de datos
    def inicializar_tabla(self):
        # Configurar el modelo inicial de la tabla y su estructura
        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels(['Clave', 'Descripción', 'Existencia', 'Precio'])
        self.crudApp.table.setModel(self.modelo)

        # Ajustar el tamaño de las columnas de forma proporcional
        self.crudApp.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.crudApp.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Clave
        self.crudApp.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Descripción
        self.crudApp.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Existencia
        self.crudApp.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Precio

        # Conectar señal para edición de celdas
        self.modelo.itemChanged.connect(self.actualizar_producto)
        # Permitir menú contextual
        self.crudApp.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.crudApp.table.customContextMenuRequested.connect(self.mostrar_menu_contextual)
    
    def mostrar_menu_contextual(self, position):
        # Crear el menú contextual
        menu = QMenu()
        copiar_accion = menu.addAction("Copiar")
        copiar_accion.triggered.connect(self.copiar_seleccion)
        
        # Mostrar el menú contextual en la posición del cursor
        menu.exec(self.crudApp.table.viewport().mapToGlobal(position))
    
    def columnas(self):
        clave = self.crudApp.claveLabel.text()
        descripcion = self.crudApp.descripcionLabel.text()
        existencia = self.crudApp.existenciaLabel.text()
        precio = self.crudApp.precioLabel.text()
        return clave, descripcion, existencia, precio
    
    def seleccionar_producto(self):
        indice_seleccionado = self.crudApp.table.selectionModel().currentIndex()
        if indice_seleccionado.isValid():
            fila = indice_seleccionado.row()
            clave = self.modelo.item(fila, 0).text()
            descripcion = self.modelo.item(fila, 1).text()
            existencia = self.modelo.item(fila, 2).text()
            precio = self.modelo.item(fila, 3).text()
            print(f"Fila seleccionada: Clave: {clave}, Descripción: {descripcion}, Existencia: {existencia}, Precio: {precio}")

    # Listar todos los productos
    def listar_productos(self):
        # Recargar datos en el modelo sin crear uno nuevo
        producto_base = ProductoBase()
        productos = producto_base.listar_productos()

        # Limpiar datos existentes en el modelo
        self.modelo.removeRows(0, self.modelo.rowCount())

        # Agregar nuevas filas al modelo
        for producto in productos:
            clave, descripcion, existencia, precio = producto
            self.modelo.appendRow([
                QStandardItem(clave),
                QStandardItem(descripcion),
                QStandardItem(str(existencia)),
                QStandardItem(f"{precio:.2f}")
            ])

        # Ajustar el tamaño de las columnas solo una vez
        self.crudApp.table.horizontalHeader().setStretchLastSection(True)
        
    # Guardar un nuevo producto
    def guardar_producto(self):
        clave, descripcion, existencia, precio = self.columnas()
        if self.validar_campos(clave, descripcion, existencia, precio):
            producto_base = ProductoBase()
            producto_base.producto = Producto(clave=clave, descripcion=descripcion, existencia=int(existencia), precio=float(precio))
            producto_base.guardar_producto()
            self.listar_productos()
            self.limpiar_campos()
        else:
            self.mostrar_mensaje("Error", "Verifica los campos ingresados.")
    
    # Actualizar un producto
    def actualizar_producto(self, item):
        # Desconectar la señal para evitar ciclo de actualización
        self.modelo.itemChanged.disconnect(self.actualizar_producto)
        
        fila = item.row()
        clave = self.modelo.item(fila, 0).text()
        descripcion = self.modelo.item(fila, 1).text()
        existencia = self.modelo.item(fila, 2).text()
        precio = self.modelo.item(fila, 3).text()
        
        if self.validar_campos(clave, descripcion, existencia, precio):
            producto_base = ProductoBase()
            producto_base.producto = Producto(clave=clave, descripcion=descripcion, existencia=int(existencia), precio=float(precio))
            producto_base.actualizar_producto()
            self.resaltar_fila(fila)  # Resaltar la fila modificada
        else:
            self.mostrar_mensaje("Error", "Verifica que los campos sean válidos.")

        # Reconectar la señal después de la actualización
        self.modelo.itemChanged.connect(self.actualizar_producto)

    def resaltar_fila(self, fila):
        # Cambiar el fondo de la fila completa al color deseado
        for col in range(self.modelo.columnCount()):
            item = self.modelo.item(fila, col)
            item.setBackground(QColor("#aed581"))

    # Eliminar un producto
    def eliminar_producto(self):
        clave = self.crudApp.claveLabel.text()
        if clave:
            producto_base = ProductoBase()
            producto_base.eliminar_producto(clave)
            self.listar_productos()
            self.limpiar_campos()
        else:
            self.mostrar_mensaje("Error", "Ingresa la clave del producto a eliminar.")

    # Buscar productos por descripción
    def buscar_producto(self):
        clave = self.crudApp.claveLabel.text()
        descripcion = self.crudApp.descripcionLabel.text()
        _, search = self.validar_campos(clave, descripcion, '', '', all=False)
        if _:
            producto_base = ProductoBase()
            productos = producto_base.buscar_productos(search)
            if productos:
                self.modelo.removeRows(0, self.modelo.rowCount())
                
                for producto in productos:
                    clave, descripcion, existencia, precio = producto
                    self.modelo.appendRow([
                        QStandardItem(clave),
                        QStandardItem(descripcion),
                        QStandardItem(str(existencia)),
                        QStandardItem(f"{precio:.2f}")
                    ])
                self.crudApp.table.horizontalHeader().setStretchLastSection(True)
            else:
                self.mostrar_mensaje("Error", "Producto no encontrado.")
        else:
            self.mostrar_mensaje("Error", "Ingresa la clave o descripción del producto a buscar.")

    def contar_productos(self):
        producto_base = ProductoBase()
        cantidad = producto_base.contar_productos_totaales()
        self.mostrar_mensaje("Cantidad de productos", f"Total de productos: {cantidad}")