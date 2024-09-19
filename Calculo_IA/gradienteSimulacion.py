import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sympy as sp

class GradienteSimulacion:
    def __init__(self, func_expr):
        self.func_expr = func_expr
        self.config = self.settings()
        self.init_pygame_opengl()
        self.define_function()
        self.initialize_variables()
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 18)
        self.show_axes = True  # Variable para controlar la visualización de los ejes
        self.show_contours = False  # Para mostrar/ocultar curvas de nivel
        self.show_vector_field = False  # Para mostrar/ocultar campo vectorial
        self.main_loop()

    def settings(self):
        config = {
            'window_size': (1280, 720),
            'background_color': (0.0, 0.0, 0.0, 1.0),
            'surface_color': (232/255, 175/255, 252/255, 0.3),  # Color de la superficie
            'gradient_color': (175/255, 252/255, 251/255),  # Color del gradiente
            'path_color': (1.0, 1.0, 0.0),
            'axes_color': (1.0, 1.0, 1.0),
            'step_size': 0.009,  # Tamaño del paso
            'max_iterations': 1000,  # Número máximo de iteraciones
            'zoom_speed': 1.0,  # Velocidad de zoom
        }
        return config

    def init_pygame_opengl(self):
        pygame.init()
        pygame.display.set_mode(self.config['window_size'], DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Simulación de Gradiente")
        glutInit()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        gluPerspective(45, (self.config['window_size'][0] / self.config['window_size'][1]), 0.1, 100.0)
        glTranslatef(0.0, 0.0, -15)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)  # Deshabilitar iluminación

    def define_function(self):
        x_sym, y_sym = sp.symbols('x y')
        func_expr = self.func_expr
        grad_expr = [sp.diff(func_expr, var) for var in (x_sym, y_sym)]
        self.func = sp.lambdify((x_sym, y_sym), func_expr, 'numpy')
        self.grad = sp.lambdify((x_sym, y_sym), grad_expr, 'numpy')

    def initialize_variables(self):
        self.rotation_x = self.rotation_y = 0
        self.mouse_down = False
        self.last_mouse_x = self.last_mouse_y = 0
        self.zoom_level = -15  # Nivel de zoom inicial
        self.pos = [np.random.uniform(-5, 5), np.random.uniform(-5, 5)]
        self.path = [tuple(self.pos)]
        self.clock = pygame.time.Clock()
        self.iterations = 0
        self.simulation_done = False
        self.simulation_active = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_down = True
                    self.last_mouse_x, self.last_mouse_y = event.pos
                elif event.button == 4:  # Rueda hacia arriba
                    self.zoom_level += self.config['zoom_speed']
                elif event.button == 5:  # Rueda hacia abajo
                    self.zoom_level -= self.config['zoom_speed']
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_down:
                    mouse_x, mouse_y = event.pos
                    self.rotation_x += (mouse_y - self.last_mouse_y) * 0.2
                    self.rotation_y += (mouse_x - self.last_mouse_x) * 0.2
                    self.last_mouse_x, self.last_mouse_y = mouse_x, mouse_y
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.simulation_active = not self.simulation_active  # Iniciar o detener simulación
                elif event.key == pygame.K_r:
                    self.pos = [np.random.uniform(-5, 5), np.random.uniform(-5, 5)]  # Reiniciar posición
                    self.path = [tuple(self.pos)]
                    self.iterations = 0
                    self.simulation_done = False
                    self.simulation_active = False
                elif event.key == pygame.K_e:
                    self.show_axes = not self.show_axes  # Ocultar/mostrar ejes
                elif event.key == pygame.K_c:
                    self.show_contours = not self.show_contours  # Activa/desactiva curvas de nivel
                elif event.key == pygame.K_v:
                    self.show_vector_field = not self.show_vector_field  # Activa/desactiva campo vectorial

    def update_simulation(self):
        if self.simulation_active and not self.simulation_done:
            grad_x, grad_y = self.grad(self.pos[0], self.pos[1])
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            if magnitude == 0 or self.iterations >= self.config['max_iterations']:
                self.simulation_done = True
                self.simulation_active = False
                return
            grad_x /= magnitude
            grad_y /= magnitude
            self.pos[0] += self.config['step_size'] * grad_x
            self.pos[1] += self.config['step_size'] * grad_y
            self.path.append(tuple(self.pos))
            self.iterations += 1

    def draw_axes(self):
        if self.show_axes:
            glColor3f(*self.config['axes_color'])
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

    def draw_labels(self):
        if self.show_axes:
            glColor3f(1.0, 1.0, 1.0)
            glRasterPos3f(11, 0, 0)
            for c in "X":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))  # type: ignore
            glRasterPos3f(0, 11, 0)
            for c in "Y":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))  # type: ignore
            glRasterPos3f(0, 0, 11)
            for c in "Z":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))  # type: ignore

    def draw_surface(self):
        glColor4f(*self.config['surface_color'])
        glEnable(GL_BLEND)
        for x in np.arange(-5, 5, 0.5):
            glBegin(GL_LINE_STRIP)
            for y in np.arange(-5, 5, 0.5):
                z = self.func(x, y)
                glVertex3f(x, y, z)
            glEnd()
        for y in np.arange(-5, 5, 0.5):
            glBegin(GL_LINE_STRIP)
            for x in np.arange(-5, 5, 0.5):
                z = self.func(x, y)
                glVertex3f(x, y, z)
            glEnd()



    def draw_contours(self):
        pass



    def draw_vector_field(self):
        """ Dibujar campo vectorial """
        if self.show_vector_field:
            glColor3f(1.0, 0.0, 0.0)  # Rojo para los vectores del campo
            for x in np.arange(-5, 5, 0.5):
                for y in np.arange(-5, 5, 0.5):
                    grad_x, grad_y = self.grad(x, y)
                    glBegin(GL_LINES)
                    glVertex3f(x, y, self.func(x, y))
                    glVertex3f(x + grad_x * 0.1, y + grad_y * 0.1, self.func(x, y))
                    glEnd()

    def draw_path(self):
        glColor3f(*self.config['path_color'])
        glBegin(GL_LINE_STRIP)
        for point in self.path:
            x, y = point
            z = self.func(x, y)
            glVertex3f(x, y, z)
        glEnd()

    def draw_current_point(self):
        glColor3f(*self.config['gradient_color'])
        glPointSize(10)
        glBegin(GL_POINTS)
        x, y = self.pos
        z = self.func(x, y)
        glVertex3f(x, y, z)
        glEnd()

    def render_text(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.config['window_size'][0], 0, self.config['window_size'][1])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        # Preparar el texto a mostrar
        func_text = f"Función: {sp.pretty(self.func_expr)}"
        pos_text = f"Posición: x = {self.pos[0]:.3f}, y = {self.pos[1]:.3f}"
        func_value = self.func(self.pos[0], self.pos[1])
        func_value_text = f"Valor de la función: {func_value:.3f}"
        grad_x, grad_y = self.grad(self.pos[0], self.pos[1])
        grad_text = f"Gradiente: ({grad_x:.3f}, {grad_y:.3f})"
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        grad_magnitude_text = f"Magnitud del gradiente: {grad_magnitude:.3f}"
        iterations_text = f"Iteraciones: {self.iterations}"
        simulation_status = "En ejecución" if self.simulation_active else "Pausada"
        status_text = f"Estado de la simulación: {simulation_status}"
        controls1 = "Controles: Espacio (Iniciar/Detener)"
        controls2 = "R (Reiniciar)"
        controls3 = "E (Ocultar/Mostrar ejes)"
        controls4 = "V (Ocultar/Mostrar campo vectorial)"

        # Posiciones para el texto
        texts = [func_text, pos_text, func_value_text, grad_text, grad_magnitude_text, iterations_text, simulation_status, controls1, controls2, controls3, controls4]
        y_offset = 20
        for i, text in enumerate(texts):
            self.draw_text(text, (10, y_offset + i * 20))

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_text(self, text, position, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        glWindowPos2d(position[0], self.config['window_size'][1] - position[1])
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def render(self):
        glClearColor(*self.config['background_color'])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.config['window_size'][0] / self.config['window_size'][1]), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.zoom_level)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        self.draw_axes()
        self.draw_labels()
        self.draw_surface()
        self.draw_contours()  # Dibujar curvas de nivel si están activadas
        self.draw_vector_field()  # Dibujar campo vectorial si está activado
        self.draw_path()
        self.draw_current_point()
        self.render_text()

    def main_loop(self):
        while True:
            self.handle_events()
            self.update_simulation()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)

# -------------------------------------------------------------

# Define aquí tu función simbólica
x, y = sp.symbols('x y')
func_expr = x**2 - y**2
simulacion = GradienteSimulacion(func_expr)
