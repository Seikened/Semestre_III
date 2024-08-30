from uno import *
from dos import *
from tres import *

def menu():
    seguir = True
    while seguir:
        print(f'''
              1. Saludo
              2. Sumar
              3. Calcular distancia
              4. Salir''')
        opcion = int(input("Introduce una opción en numero: "))
        
        if opcion == 4:
            seguir = False
        elif opcion == 1:
            saludo()
        elif opcion == 2:
            sumar()
        elif opcion == 3:
            calcularDistancia()
        else:
            print("Opción no válida")

if __name__ == "__main__":
    menu()