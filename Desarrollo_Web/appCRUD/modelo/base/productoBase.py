from modelo.base.product import Producto
from modelo.conexion import Conexion


class ProductoBase:
    def __init__(self):
        self.producto = Producto()
        self.status = ''

    def guardar_producto(self):
        """Guarda un producto en la base de datos."""
        base_datos = Conexion()
        base_datos.conexion()
        cursor = base_datos.conexion.cursor()
        
        clave = self.producto.clave
        descripcion = self.producto.descripcion
        existencia = self.producto.existencia
        precio = self.producto.precio
        
        query = "CALL sp_insertar_producto(%s, %s, %s, %s);"
        cursor.execute(query, (clave, descripcion, existencia, precio))
        
        # Commit de la transacción
        base_datos.conexion.commit()
        
        self.status = f"Producto {clave} | {descripcion} | {existencia} | {precio} guardado"
        base_datos.cerrar_conexion()

    def actualizar_producto(self):
        """Actualiza un producto existente en la base de datos."""
        base_datos = Conexion()
        base_datos.conexion()
        cursor = base_datos.conexion.cursor()
        
        clave = self.producto.clave
        descripcion = self.producto.descripcion
        existencia = self.producto.existencia
        precio = self.producto.precio
        
        query = "CALL sp_modificar_producto(%s, %s, %s, %s);"
        cursor.execute(query, (clave, descripcion, existencia, precio))
        
        # Commit de la transacción
        base_datos.conexion.commit()
        
        self.status = f"Producto {clave} | {descripcion} | {existencia} | {precio} actualizado"
        base_datos.cerrar_conexion()

    def eliminar_producto(self, clave_producto):
        """Elimina un producto de la base de datos por su clave."""
        base_datos = Conexion()
        base_datos.conexion()
        cursor = base_datos.conexion.cursor()
        
        query = "CALL sp_eliminar_producto(%s);"
        cursor.execute(query, (clave_producto,))
        
        # Commit de la transacción
        base_datos.conexion.commit()
        
        self.status = f"Producto {clave_producto} eliminado"
        base_datos.cerrar_conexion()

    def buscar_productos(self, producto_buscar):
        """Busca productos en la base de datos por descripción o clave."""
        base_datos = Conexion()
        base_datos.conexion()
        cursor = base_datos.conexion.cursor()
        
        query = "SELECT * FROM fn_buscar_producto(%s);"
        cursor.execute(query, (producto_buscar,))
        
        productos = cursor.fetchall()
        print(f"Buscando {producto_buscar}: {productos}")
        
        if productos:
            for producto in productos:
                print(f"Clave: {producto[0]} | Descripción: {producto[1]} | Existencia: {producto[2]} | Precio: {producto[3]}")
                self.producto.clave = producto[0]
                self.producto.descripcion = producto[1]
                self.producto.existencia = producto[2]
                self.producto.precio = producto[3]
        else:
            self.status = f"Producto {producto_buscar} no encontrado"
        
        self.status = f"Búsqueda de {producto_buscar} completada"
        base_datos.cerrar_conexion()

    def listar_productos(self):
        """Lista todos los productos de la base de datos."""
        base_datos = Conexion()
        base_datos.conexion()
        cursor = base_datos.conexion.cursor()
        query = 'SELECT * FROM fn_listar_productos();'
        cursor.execute(query)
        filas = cursor.fetchall()
        base_datos.cerrar_conexion()
        return filas