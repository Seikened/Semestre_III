import numpy as np

# Matriz incompleta de Sudoku (proposición inicial)
sudoku = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Matriz resuelta de Sudoku (proposición final)
sudoku_resuelto = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9]
]

def digito_en_fila_o_col(arreglo, digito):
    """ 
    Proposición lógica: Verificar si un dígito está presente en la fila o columna.
    Si el dígito está presente en la fila o columna, la proposición es verdadera.
    """
    return digito in arreglo

def verificar_fila_o_col(arreglo):
    """ 
    Proposición lógica: Verificar si en una fila o columna están presentes los números del 1 al 9.
    Para que una fila o columna sea válida, debe cumplir la condición de que contenga todos los números del 1 al 9.
    """
    # Lista de proposiciones: cada número del 1 al 9 está presente
    lista = [digito_en_fila_o_col(arreglo, digito + 1) for digito in range(9)]
    # Si todas las proposiciones son verdaderas, entonces la fila o columna es válida
    return all(lista)

def verificar_bloque(matriz, fila, col):
    """
    Proposición lógica: Verificar si un bloque 3x3 tiene todos los números del 1 al 9.
    Si el bloque tiene los números del 1 al 9, la proposición es verdadera.
    """
    # Aplanar el bloque para tratarlo como una lista
    bloque = matriz[fila:fila+3, col:col+3].flatten()
    # Reusar la verificación de fila o columna para validar el bloque
    return verificar_fila_o_col(bloque)

def verificar_sudoku(matriz):
    """
    Verificación de proposiciones lógicas:
    - Cada fila debe contener los números del 1 al 9 (proposición 1)
    - Cada columna debe contener los números del 1 al 9 (proposición 2)
    - Cada bloque 3x3 debe contener los números del 1 al 9 (proposición 3)
    Si todas las proposiciones son verdaderas, entonces el Sudoku es válido.
    """
    # Verificar cada fila (proposición 1)
    for i in range(9):
        if not verificar_fila_o_col(matriz[i]):
            return False  # Si alguna fila no es válida, el Sudoku es falso
    
    # Verificar cada columna (proposición 2)
    for i in range(9):
        if not verificar_fila_o_col(matriz[:, i]):  # Verificar la columna 'i'
            return False  # Si alguna columna no es válida, el Sudoku es falso
    
    # Verificar bloques 3x3 (proposición 3)
    for i in range(0, 9, 3):  # Iterar por bloques de 3 en 3
        for j in range(0, 9, 3):
            if not verificar_bloque(matriz, i, j):
                return False  # Si algún bloque no es válido, el Sudoku es falso
    
    # Si todas las proposiciones son verdaderas, el Sudoku es válido
    return True

# Convertir el Sudoku a un arreglo de NumPy para facilitar la indexación
sudoku = np.array(sudoku)

# Imprimir el Sudoku inicial
print("Sudoku inicial:")
print(sudoku)

# Verificar el Sudoku inicial (validar proposiciones)
verificarSudoku = verificar_sudoku(sudoku)
print("¿El Sudoku inicial es válido?", verificarSudoku)

# Convertir la solución de Sudoku a un arreglo de NumPy
sudoku_resuelto = np.array(sudoku_resuelto)

# Imprimir el Sudoku resuelto
print("Sudoku resuelto:")
print(sudoku_resuelto)

# Verificar el Sudoku resuelto (validar proposiciones)
verificarSudokuR = verificar_sudoku(sudoku_resuelto)
print("¿El Sudoku resuelto es válido?", verificarSudokuR)