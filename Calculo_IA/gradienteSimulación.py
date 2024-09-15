import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sympy as sp

def settings():
    config = {
        'window_size': (1920, 1080),
        'background_color': (0.0, 0.0, 0.0, 1.0),
        # Coloeres en formato RGB (232, 175, 252)
        'surface_color': (232/255, 175/255, 252/255, 0.3),  # Color de la superficie
        # Coloeres en formato RGB (175, 252, 251)
        'gradient_color': (175/255, 252/255, 251/255),  # Color del gradiente
        'path_color': (1.0, 1.0, 0.0),
        'axes_color': (1.0, 1.0, 1.0),
        'step_size': 0.009,  # Reducimos el tamaño del paso
        'max_iterations': 1000,  # Aumentamos el número máximo de iteraciones
        'zoom_speed': 1.0,  # Velocidad de zoom
    }
    return config



def init(config):
    pygame.init()
    pygame.display.set_mode(config['window_size'], DOUBLEBUF | OPENGL)
    glutInit()  # Inicializamos GLUT
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    gluPerspective(45, (config['window_size'][0] / config['window_size'][1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -15)  # Alejamos la cámara
    glEnable(GL_DEPTH_TEST)

def define_function():
    x_sym, y_sym = sp.symbols('x y')
    # Define aquí tu función
    func_expr = x_sym**2 + y_sym**2
    grad_expr = [sp.diff(func_expr, var) for var in (x_sym, y_sym)]
    # Convierte las expresiones simbólicas en funciones numéricas
    func = sp.lambdify((x_sym, y_sym), func_expr, 'numpy')
    grad = sp.lambdify((x_sym, y_sym), grad_expr, 'numpy')
    return func, grad

def draw_axes(config):
    glColor3f(*config['axes_color'])
    glBegin(GL_LINES)
    axis_length = 10
    # Eje X
    glVertex3f(-axis_length, 0, 0)
    glVertex3f(axis_length, 0, 0)
    # Eje Y
    glVertex3f(0, -axis_length, 0)
    glVertex3f(0, axis_length, 0)
    # Eje Z
    glVertex3f(0, 0, -axis_length)
    glVertex3f(0, 0, axis_length)
    glEnd()

def draw_labels():
    # Función para dibujar etiquetas en los ejes
    glColor3f(1.0, 1.0, 1.0)  # Color blanco para las etiquetas
    # Habilitamos el uso de texturas 2D
    glEnable(GL_TEXTURE_2D)
    # Eje X
    glRasterPos3f(11, 0, 0)
    for c in "X":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    # Eje Y
    glRasterPos3f(0, 11, 0)
    for c in "Y":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    # Eje Z
    glRasterPos3f(0, 0, 11)
    for c in "Z":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    glDisable(GL_TEXTURE_2D)

def draw_surface(func, config):
    glColor4f(*config['surface_color'])  # Usamos glColor4f para incluir alfa
    for x in np.arange(-5, 5, 0.5):
        glBegin(GL_LINE_STRIP)
        for y in np.arange(-5, 5, 0.5):
            z = func(x, y)
            glVertex3f(x, y, z)
        glEnd()
    for y in np.arange(-5, 5, 0.5):
        glBegin(GL_LINE_STRIP)
        for x in np.arange(-5, 5, 0.5):
            z = func(x, y)
            glVertex3f(x, y, z)
        glEnd()

def update_position(pos, grad, config):
    grad_x, grad_y = grad(pos[0], pos[1])
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    if magnitude == 0:
        return pos, True  # Gradiente cero, hemos llegado al punto crítico
    # Normalizar el gradiente
    grad_x /= magnitude
    grad_y /= magnitude
    # Actualizar la posición
    pos[0] += grad_x * config['step_size']
    pos[1] += grad_y * config['step_size']
    return pos, False

def draw_path(path, func, config):
    glColor3f(*config['path_color'])
    glBegin(GL_LINE_STRIP)
    for point in path:
        x, y = point
        z = func(x, y)
        glVertex3f(x, y, z)
    glEnd()

def main():
    config = settings()
    init(config)
    func, grad = define_function()

    global rotation_x, rotation_y, mouse_down, last_mouse_x, last_mouse_y, zoom_level
    rotation_x = rotation_y = 0
    mouse_down = False
    last_mouse_x = last_mouse_y = 0
    zoom_level = -15  # Nivel de zoom inicial

    # Posición inicial aleatoria
    pos = [np.random.uniform(-5, 5), np.random.uniform(-5, 5)]
    path = [tuple(pos)]  # Lista para almacenar la trayectoria

    clock = pygame.time.Clock()
    iterations = 0
    simulation_done = False  # Para saber si la simulación ha terminado
    simulation_active = False  # Controla si la simulación está activa

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # Eventos del mouse para rotar la escena
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_mouse_x, last_mouse_y = event.pos
                # Control de zoom con la rueda del mouse
                elif event.button == 4:  # Rueda hacia arriba
                    zoom_level += config['zoom_speed']
                elif event.button == 5:  # Rueda hacia abajo
                    zoom_level -= config['zoom_speed']

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            if event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    mouse_x, mouse_y = event.pos
                    rotation_x += (mouse_y - last_mouse_y) * 0.2
                    rotation_y += (mouse_x - last_mouse_x) * 0.2
                    last_mouse_x, last_mouse_y = mouse_x, mouse_y

            # Controlar la simulación con la tecla 's' para iniciar/pausar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    simulation_active = not simulation_active  # Cambia el estado de la simulación
                # Reiniciar la simulación con la tecla 'r'
                if event.key == pygame.K_r:
                    pos = [np.random.uniform(-5, 5), np.random.uniform(-5, 5)]
                    path = [tuple(pos)]
                    iterations = 0
                    simulation_done = False
                    simulation_active = False

        # Actualizar la posición siguiendo el gradiente solo si la simulación está activa
        if simulation_active and iterations < config['max_iterations'] and not simulation_done:
            pos, simulation_done = update_position(pos, grad, config)
            path.append(tuple(pos))
            iterations += 1

        glClearColor(*config['background_color'])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Configuración de la vista y la proyección
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (config['window_size'][0] / config['window_size'][1]), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, zoom_level)  # Aplicamos el zoom
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        draw_axes(config)  # Dibujar los ejes coordenados
        draw_labels()      # Dibujar las etiquetas de los ejes
        draw_surface(func, config)
        # Eliminamos la llamada a draw_gradient para quitar las líneas rojas
        draw_path(path, func, config)

        # Dibujar el punto actual
        glColor3f(0, 1, 0)  # Verde para el punto
        glPointSize(10)
        glBegin(GL_POINTS)
        x, y = pos
        z = func(x, y)
        glVertex3f(x, y, z)
        glEnd()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()