import random as r
import numpy as np




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

def digito_en_fila_o_col(arreglo,digito):
    return digito in arreglo


def verificar_fila_o_col(arreglo):
    # # opcion 1
    # for i in range(9):
    #     if digito_en_fila_o_col(arreglo,i+1):
    #         return True
    # return False


    # opcion 2
    lista = [digito_en_fila_o_col(arreglo,digito) for digito in range(9)]
    return all(lista)

def verificar_sudoku(matriz):
    # verificar fila
    for i in range(9):
        if not verificar_fila_o_col(matriz[i]):
            return False
    # verificar columna
    for i in range(9):
        if not verificar_fila_o_col(matriz[:,i]):
            return False
    # verifica bloques
    for i in range(3):
        for j in range(3):
            fila = i*3
            col = j*3
            bloque = matriz[fila:fila+3,col:col+3]
            if not verificar_fila_o_col(bloque):
                return False
    return True

sudoku = np.array(sudoku)

print(sudoku)


verificarZudoku = verificar_sudoku(sudoku)
print(verificarZudoku)

sudoku_resuelto = np.array(sudoku_resuelto)

print(sudoku_resuelto)

verificarZudokuR = verificar_sudoku(sudoku_resuelto)
print(verificarZudokuR)