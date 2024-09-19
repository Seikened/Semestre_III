import pygame
import numpy as np
import time

pygame.init()

ancho = 600
alto = 600
screen = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption('Animación de Sudoku')

blanco = (255, 255, 255)
negro = (0, 0, 0)
verde = (0, 255, 0)
amarillo = (255, 255, 102)
azul = (102, 204, 255)
gris = (200, 200, 200)
fondo_gradiente = [(150, 150, 255), (100, 100, 255), (50, 50, 255)]

font = pygame.font.Font(None, 36)

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

tamaño_celda = ancho // 9

def dibujar_fondo(screen, colores):
    for i, color in enumerate(colores):
        pygame.draw.rect(screen, color, (0, i * alto // len(colores), ancho, alto // len(colores)))

def dibujar_sudoku(sudoku, correctas):
    for fila in range(9):
        for col in range(9):
            num = sudoku[fila][col]
            x = col * tamaño_celda
            y = fila * tamaño_celda
            
            if (fila, col) in correctas:
                color = [amarillo[i] + (verde[i] - amarillo[i]) * (len(correctas) / 81) for i in range(3)]
                pygame.draw.rect(screen, color, (x, y, tamaño_celda, tamaño_celda))
            else:
                pygame.draw.rect(screen, blanco, (x, y, tamaño_celda, tamaño_celda))
            
            if num != 0:
                sombra = font.render(str(num), True, gris)
                screen.blit(sombra, (x + 22, y + 12))
                
                num_surface = font.render(str(num), True, negro)
                screen.blit(num_surface, (x + 20, y + 10))
    
    for i in range(10):
        line_thickness = 5 if i % 3 == 0 else 2
        pygame.draw.line(screen, negro, (0, i * tamaño_celda), (ancho, i * tamaño_celda), line_thickness)
        pygame.draw.line(screen, negro, (i * tamaño_celda, 0), (i * tamaño_celda, alto), line_thickness)

def verificar_sudoku(matriz):
    correctas = set()

    for fila in range(9):
        if sorted(matriz[fila]) == list(range(1, 10)):
            for col in range(9):
                correctas.add((fila, col))
    
    for col in range(9):
        if sorted([matriz[fila][col] for fila in range(9)]) == list(range(1, 10)):
            for fila in range(9):
                correctas.add((fila, col))

    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            bloque = [matriz[x][y] for x in range(i, i+3) for y in range(j, j+3)]
            if sorted(bloque) == list(range(1, 10)):
                for x in range(i, i+3):
                    for y in range(j, j+3):
                        correctas.add((x, y))

    return correctas

def animar_solucion(sudoku, sudoku_resuelto):
    correctas = set()
    
    for fila in range(9):
        for col in range(9):
            if sudoku[fila][col] == 0:
                sudoku[fila][col] = sudoku_resuelto[fila][col]
                correctas = verificar_sudoku(sudoku)
                
                dibujar_fondo(screen, fondo_gradiente)
                dibujar_sudoku(sudoku, correctas)
                pygame.display.flip()
                time.sleep(0.1)

def main():
    clock = pygame.time.Clock()
    ejecutando = True
    
    while ejecutando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ejecutando = False
        
        animar_solucion(sudoku, sudoku_resuelto)
        
        pygame.display.flip()
        
        clock.tick(30)
        
        time.sleep(3)
        ejecutando = False
    
    pygame.quit()

if __name__ == "__main__":
    main()
