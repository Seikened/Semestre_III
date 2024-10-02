from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QHeaderView
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
        self.mostrar_productos()
        QTimer.singleShot(1000, self.limpiar_campos)

    def loadUI(self):
        self.crudApp = uic.loadUi(ui, self)
        self.setFixedSize(self.width(), self.height()) 

        # Conectar botones a funciones
        self.crudApp.readBtn.clicked.connect(self.mostrar_productos)
        self.crudApp.createBtn.clicked.connect(self.guardar_producto)
        self.crudApp.updateBtn.clicked.connect(self.actualizar_producto)
        self.crudApp.deleteBtn.clicked.connect(self.eliminar_producto)

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

        # Conectar señal para detección de selección
        self.crudApp.table.selectionModel().selectionChanged.connect(self.seleccionar_producto)

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

    def mostrar_productos(self):
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

    def guardar_producto(self):
        clave, descripcion, existencia, precio = self.columnas()
        if self.validar_campos(clave, descripcion, existencia, precio):
            producto_base = ProductoBase()
            producto_base.producto = Producto(clave=clave, descripcion=descripcion, existencia=int(existencia), precio=float(precio))
            producto_base.guardar_producto()
            self.mostrar_productos()
            self.limpiar_campos()
        else:
            self.mostrar_mensaje("Error", "Verifica los campos ingresados.")

    def actualizar_producto(self, item):
        fila = item.row()
        clave = self.modelo.item(fila, 0).text()
        descripcion = self.modelo.item(fila, 1).text()
        existencia = self.modelo.item(fila, 2).text()
        precio = self.modelo.item(fila, 3).text()
        
        if self.validar_campos(clave, descripcion, existencia, precio):
            producto_base = ProductoBase()
            producto_base.producto = Producto(clave=clave, descripcion=descripcion, existencia=int(existencia), precio=float(precio))
            producto_base.actualizar_producto()
            self.mostrar_productos()
        else:
            self.mostrar_mensaje("Error", "Verifica los campos ingresados.")

    def eliminar_producto(self):
        clave = self.crudApp.claveLabel.text()
        if clave:
            producto_base = ProductoBase()
            producto_base.eliminar_producto(clave)
            self.mostrar_productos()
            self.limpiar_campos()
        else:
            self.mostrar_mensaje("Error", "Ingresa la clave del producto a eliminar.")
    
    def validar_campos(self, clave, descripcion, existencia, precio):
        if not clave or not descripcion or not existencia or not precio:
            return False
        try:
            int(existencia)
            float(precio)
        except ValueError:
            return False
        return True

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
