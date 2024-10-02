import psycopg2

class Conexion():
    def __init__(self):
        self.queryResult = None
        

    def operation(self, query):
        self.conexion()
        self.query(query)
        self.cerrar_conexion()

    def conexion(self):
        try:
            self.conexion = psycopg2.connect(
                host="localhost",
                database="fernando",
                user="postgres",
                password="flfyarmi343"
            )
            self.cursor = self.conexion.cursor()
            print("Conexión exitosa")
        except Exception as error:
            print(f"Error al conectar a PostgreSQL: {error}")
    
    def cerrar_conexion(self):
        self.cursor.close()
        self.conexion.close()
        print("Conexión cerrada")
    
    def query(self, query):
        try:
            self.cursor.execute(query)
            self.queryResult = self.cursor.fetchall()
            print(self.queryResult)
        except Exception as error:
            print(f"Error en la query: {error}")
    
    def get_tables(self):
        self.conexion()
        self.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        self.cerrar_conexion()
        return self.queryResult
    
    def get_columns(self, table):
        self.conexion()
        self.query(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
        self.cerrar_conexion()
        return self.queryResult
    
    def select(self, table):
        self.conexion()
        self.query(f"SELECT * FROM {table}")
        self.queryResult = self.cursor.fetchall()
        self.cerrar_conexion()
        return self.queryResult





if __name__ == "__main__":
    conexion = Conexion()
    conexion.get_tables()
    conexion.select("productos")
    print(conexion.queryResult)