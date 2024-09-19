def mi_generador():
    print("Generador iniciado")
    for i in range(3):
        print(f"Yielding {i}")
        yield i  # Se pausa y devuelve i
    print("Generador finalizado")

# Crear el generador
gen = mi_generador()

# Iterar sobre el generador
for valor in gen:
    print(f"Valor recibido: {valor}")
    
    for i in range(3):
        print(f"Yielding {i}")
        gen.send(i)
        ((((((((((((()))))))))))))