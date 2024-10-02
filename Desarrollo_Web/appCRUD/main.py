import sys
from modelo.base.productoBase import ProductoBase
from PyQt6.QtWidgets import QApplication
from modelo.base.product import Producto
import time
from load.interfaz import ProductoApp


def test():
    producto_base = ProductoBase()
    
    # Listar todos los productos
    print("Listando todos los productos:")
    producto_base.listar_productos()
    
    # Crear un nuevo producto
    print("\nGuardando un nuevo producto:")
    producto_base.producto.clave = 'FX-T2'
    producto_base.producto.descripcion = 'Lampara de lava'
    producto_base.producto.existencia = 10
    producto_base.producto.precio = 99.99
    producto_base.guardar_producto()
    print(producto_base.status)
    
    producto_base.listar_productos()
    
    for i in range(100):
        producto_base.producto.clave = f'FX-Tt{i}'
        producto_base.producto.descripcion = f'Laptop {i}'
        producto_base.producto.existencia = 10
        producto_base.producto.precio = 99.99
        producto_base.guardar_producto()
    
    producto_base.listar_productos()
    
    # delay of the 20s but the time remaining needs to be displayed
    for i in range(20):
        sys.stdout.write(f"\r{20 - i} seconds remaining")
        time.sleep(1)
    
    # Actualizar el producto recién creado
    print("\nActualizando el producto:")
    producto_base.producto.descripcion = 'Lampara de lava actualizada'
    producto_base.producto.existencia = 15
    producto_base.producto.precio = 109.99
    producto_base.actualizar_producto()
    print(producto_base.status)
    
    producto_base.listar_productos()

    # Buscar el producto recién actualizado
    print("\nBuscando el producto actualizado:")
    producto_base.buscar_productos('Laptop')
    producto_base.buscar_productos('Lampara')
    
    # Eliminar el producto
    print("\nEliminando el producto:")
    producto_base.eliminar_producto('FX-T2')  # Usa la `clave` para eliminar
    print(producto_base.status)
    
    for i in range(100):
        producto_base.eliminar_producto(f'FX-Tt{i}')
    
    # Listar productos nuevamente para verificar que se eliminó
    print("\nListando todos los productos después de la eliminación:")
    producto_base.listar_productos()



def main():
    app = QApplication(sys.argv)
    crud = ProductoApp()
    crud.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()