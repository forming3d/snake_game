import math
import random
import pygame
import json
import os

# Inicializar pygame
pygame.init()

# ----------------- CONSTANTES GENERALES -----------------

SCREEN_WIDTH = 400   # Ancho para móviles (vertical)
SCREEN_HEIGHT = 800  # Alto para móviles (vertical)
SCREEN_TITLE = "Hex Snake - Mobile"

HEX_RADIUS = 150.0   # Radio ajustado para formato vertical

SNAKE_SPEED = 200.0          # píxeles / segundo
SNAKE_RADIUS = 10.0          # tamaño base "pixel art"

INITIAL_SEGMENTS = 3         # nº inicial de segmentos (esferas) del cuerpo
SEGMENTS_PER_FOOD = 1         # segmentos que se agregan por cada comida
SEGMENT_SPACING = SNAKE_RADIUS * 2.2  # distancia entre segmentos

NUM_REWARDS = 5
REWARD_RADIUS = 8.0
GRAVITY = -150.0             # hacia abajo en coords locales (más suave)
REWARD_BOUNCE = 0.85         # rebote con pérdida de energía (más suave)

HEX_ROTATION_SPEED = 20.0    # grados / segundo (velocidad base)
HEX_ROTATION_CHANGE_MIN = 2.0   # tiempo mínimo entre cambios de rotación (segundos)
HEX_ROTATION_CHANGE_MAX = 5.0   # tiempo máximo entre cambios de rotación (segundos)
HEX_ROTATION_SPEED_MIN = 10.0   # velocidad mínima de rotación (grados/segundo)
HEX_ROTATION_SPEED_MAX = 40.0   # velocidad máxima de rotación (grados/segundo)

# Parallax y fondo (ajustado para móviles)
NUM_STARS = 100  # Menos estrellas para mejor rendimiento en móviles
STAR_COLOR = (255, 255, 255, 200)  # Estrellas blancas
GRID_SPACING = 30  # Grid más pequeño para móviles
GRID_COLOR = (30, 30, 50, 100)
NUM_BACKGROUND_SHAPES = 8  # Menos formas para mejor rendimiento
PARALLAX_FACTOR = 0.15  # Factor de parallax para el fondo
HEX_NOISE_POINTS = 120  # Menos puntos naranjas para móviles

# Partículas
PARTICLE_LIFETIME = 0.4  # segundos de vida de las partículas
SPARKS_PER_REWARD = 12   # número de chispas al recoger recompensa
SPARK_SPEED_MIN = 80.0   # velocidad mínima de chispas
SPARK_SPEED_MAX = 200.0  # velocidad máxima de chispas
SPARK_SIZE = 3.0         # tamaño de las chispas
FLASH_LIFETIME = 0.3     # duración del flash de rebote
FLASH_SIZE = 15.0        # tamaño del flash

# Efectos visuales: Glow, Luces y Sombras
REWARD_GLOW_LAYERS = 5   # número de capas para el glow de recompensas
REWARD_GLOW_SIZE = 10.0  # tamaño del glow de recompensas
HEX_GLOW_LAYERS = 5      # número de capas para el glow del hexágono
HEX_GLOW_SIZE = 15.0     # tamaño del glow del hexágono
LIGHT_RADIUS = 120.0     # radio de las luces dinámicas
SHADOW_OFFSET_X = 3.0    # offset de sombra en X
SHADOW_OFFSET_Y = -3.0   # offset de sombra en Y
SHADOW_ALPHA = 80        # opacidad de las sombras

STATE_PRESENTATION = "presentation"
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Archivo para guardar el mejor score
SCORE_FILE = "best_score.json"

# Colores comunes (equivalente a arcade.color)
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_AMAZON = (59, 122, 87)
COLOR_AQUAMARINE = (127, 255, 212)


# ----------------- HELPERS DE VECTORES -----------------

def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def vec_scale(a, s):
    return [a[0] * s, a[1] * s]


def vec_length(a):
    return math.hypot(a[0], a[1])


def vec_reflect(v, n):
    """Refleja el vector v contra una normal n (unitaria)."""
    dot = vec_dot(v, n)
    return [v[0] - 2 * dot * n[0], v[1] - 2 * dot * n[1]]


# ----------------- HELPERS DE PIXEL ART TEXT -----------------

# Fuente pixel art simple 5x7 (solo números y algunas letras básicas)
PIXEL_FONT = {
    '0': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    '1': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    '2': ['11110', '00001', '00001', '11110', '10000', '10000', '11111'],
    '3': ['11110', '00001', '00001', '11110', '00001', '00001', '11110'],
    '4': ['10001', '10001', '10001', '11111', '00001', '00001', '00001'],
    '5': ['11111', '10000', '10000', '11110', '00001', '00001', '11110'],
    '6': ['11110', '10000', '10000', '11110', '10001', '10001', '11110'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    '8': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    '9': ['11110', '10001', '10001', '11111', '00001', '00001', '11110'],
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'C': ['11110', '10001', '10000', '10000', '10000', '10001', '11110'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'G': ['11110', '10001', '10000', '10111', '10001', '10001', '11110'],
    'H': ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'M': ['10001', '11011', '10101', '10001', '10001', '10001', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    'O': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'S': ['11110', '10001', '10000', '11110', '00001', '10001', '11110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
    'W': ['10001', '10001', '10001', '10001', '10101', '11011', '10001'],
    'X': ['10001', '01010', '00100', '00100', '00100', '01010', '10001'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    ':': ['00000', '00100', '00000', '00000', '00000', '00100', '00000'],
    ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
    '←': ['00000', '00100', '01000', '11111', '01000', '00100', '00000'],
    '↑': ['00100', '01110', '10101', '00100', '00100', '00100', '00100'],
    '→': ['00000', '00100', '00010', '11111', '00010', '00100', '00000'],
    '↓': ['00100', '00100', '00100', '00100', '10101', '01110', '00100'],
}

def draw_pixel_text(surface, text, x, y, color, pixel_size=3):
    """
    Dibuja texto en estilo pixel art.
    surface: superficie de pygame donde dibujar
    text: texto a dibujar (solo mayúsculas y números)
    x, y: posición superior izquierda
    color: tupla RGB o RGBA
    pixel_size: tamaño de cada píxel
    """
    char_width = 6 * pixel_size  # Ancho de cada carácter (5 píxeles + 1 espacio)
    current_x = x
    
    # Convertir color RGBA a RGB si es necesario
    if len(color) == 4:
        color_rgb = color[:3]
    else:
        color_rgb = color
    
    for char in text.upper():
        if char in PIXEL_FONT:
            pattern = PIXEL_FONT[char]
            # Dibujar filas normalmente de arriba hacia abajo
            for row_idx, row in enumerate(pattern):
                for col_idx, pixel in enumerate(row):
                    if pixel == '1':
                        px = current_x + col_idx * pixel_size
                        # En pygame Y va hacia abajo, empezamos desde y y vamos sumando
                        py = y + row_idx * pixel_size
                        pygame.draw.rect(
                            surface,
                            color_rgb,
                            (int(px), int(py), pixel_size, pixel_size)
                        )
            current_x += char_width
        else:
            # Si el carácter no está en la fuente, dejar espacio
            current_x += char_width


# ----------------- FUNCIONES DE GUARDADO -----------------

def load_best_score():
    """Carga el mejor score desde el archivo."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), SCORE_FILE) if __file__ else SCORE_FILE
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                score = data.get('best_score', 0)
                print(f"Mejor score cargado: {score}")  # Debug
                return score
    except Exception as e:
        print(f"Error al cargar mejor score: {e}")
    return 0

def save_best_score(score):
    """Guarda el mejor score en el archivo."""
    try:
        data = {'best_score': score}
        file_path = os.path.join(os.path.dirname(__file__), SCORE_FILE) if __file__ else SCORE_FILE
        with open(file_path, 'w') as f:
            json.dump(data, f)
        print(f"Mejor score guardado: {score}")  # Debug
    except Exception as e:
        print(f"Error al guardar mejor score: {e}")

# ----------------- CLASE PRINCIPAL -----------------

class SnakeGame:
    def __init__(self):
        # Crear ventana de pygame
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Color de fondo
        self.bg_color = (15, 10, 25)  # Azul-púrpura oscuro

        # centro de la escena
        self.cx = SCREEN_WIDTH / 2
        self.cy = SCREEN_HEIGHT / 2

        # Geometría del hexágono en coords locales (centro = (0,0))
        self.hex_vertices_local = self._create_hexagon(HEX_RADIUS)
        self.hex_edges = self._compute_edges(self.hex_vertices_local)

        # Rotación visual del escenario
        self.hex_angle = 0.0
        self.hex_rotation_speed = HEX_ROTATION_SPEED  # Velocidad actual de rotación
        self.hex_rotation_timer = 0.0  # Temporizador para cambios aleatorios
        self.hex_rotation_change_time = random.uniform(HEX_ROTATION_CHANGE_MIN, HEX_ROTATION_CHANGE_MAX)

        # HUD / estado
        self.state = STATE_PRESENTATION  # Empezar en pantalla de presentación
        self.score = 0
        self.best_score = load_best_score()  # Cargar mejor score guardado
        
        self.snake_head_pos = [0.0, 0.0]
        self.snake_velocity = [SNAKE_SPEED, 0.0]
        self.snake_body = []  # Lista de posiciones de segmentos (esferas)
        self.last_head_pos = [0.0, 0.0]  # Para rastrear movimiento
        self.snake_path = []  # Historial de posiciones de la cabeza para que los segmentos sigan
        self.next_direction = None  # Dirección pendiente para cambiar

        self.rewards = []
        self.game_over_reason = ""

        # Fondo: estrellas y formas
        self.stars = []
        self.background_shapes = []
        self.hex_noise_points = []  # Puntos naranjas dentro del hexágono
        self._init_background()

        # Partículas
        self.particles = []  # Lista de partículas activas

        # Botón de reinicio: (left, top, width, height) - ajustado para móviles
        self.restart_button_rect = (
            SCREEN_WIDTH / 2 - 70,
            SCREEN_HEIGHT / 2 - 30,  # Se ajustará dinámicamente en draw
            140,
            40,
        )
        
        # Botón PLAY en pantalla de presentación: (left, top, width, height)
        self.play_button_rect = (
            SCREEN_WIDTH / 2 - 60,
            SCREEN_HEIGHT - 150,  # Parte inferior de la pantalla
            120,
            45,
        )

        # Cargar imagen de presentación para la pantalla inicial
        try:
            presentation_image_path = os.path.join(os.path.dirname(__file__), "assets", "presentacion.png")
            presentation_image = pygame.image.load(presentation_image_path).convert_alpha()
            # Escalar imagen para que llene toda la pantalla (ajustar a tamaño completo)
            self.presentation_image = pygame.transform.scale(presentation_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error al cargar imagen presentacion.png: {e}")
            self.presentation_image = None

        # Cargar imagen de bonificación para las recompensas
        try:
            bonus_image_path = os.path.join(os.path.dirname(__file__), "assets", "bonificacion.png")
            bonus_image = pygame.image.load(bonus_image_path).convert_alpha()
            # Escalar imagen al tamaño de las recompensas (basado en REWARD_RADIUS)
            # Usar aproximadamente 2 * REWARD_RADIUS como tamaño
            reward_size = int(REWARD_RADIUS * 2.5)  # Tamaño un poco más grande que el radio
            img_width, img_height = bonus_image.get_size()
            # Mantener aspecto de la imagen
            if img_width > img_height:
                new_width = reward_size
                new_height = int(img_height * (reward_size / img_width))
            else:
                new_height = reward_size
                new_width = int(img_width * (reward_size / img_height))
            self.bonus_image = pygame.transform.scale(bonus_image, (new_width, new_height))
        except Exception as e:
            print(f"Error al cargar imagen bonificacion.png: {e}")
            self.bonus_image = None

        # Cargar imagen del cuerpo de la serpiente (bonificacion.png con filtro verde)
        try:
            snake_body_image_path = os.path.join(os.path.dirname(__file__), "assets", "bonificacion.png")
            snake_body_image = pygame.image.load(snake_body_image_path).convert_alpha()
            # Escalar imagen al tamaño de los segmentos (basado en SNAKE_RADIUS)
            body_size = int(SNAKE_RADIUS * 2.5)  # Tamaño un poco más grande que el radio
            img_width, img_height = snake_body_image.get_size()
            # Mantener aspecto de la imagen
            if img_width > img_height:
                new_width = body_size
                new_height = int(img_height * (body_size / img_width))
            else:
                new_height = body_size
                new_width = int(img_width * (body_size / img_height))
            scaled_image = pygame.transform.scale(snake_body_image, (new_width, new_height))
            
            # Aplicar filtro verde con saturación preservando transparencia
            # Crear una nueva superficie con transparencia
            green_filtered = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            
            # Crear una máscara circular para eliminar bordes cuadrados
            mask = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            center_x, center_y = new_width // 2, new_height // 2
            radius = min(new_width, new_height) // 2
            pygame.draw.circle(mask, (255, 255, 255, 255), (center_x, center_y), radius)
            
            # Aplicar filtro verde usando pixelarray para mejor control
            pixel_array = pygame.surfarray.pixels3d(scaled_image)
            alpha_array = pygame.surfarray.pixels_alpha(scaled_image)
            mask_array = pygame.surfarray.pixels_alpha(mask)
            
            # Crear array para la imagen filtrada
            filtered_pixels = pygame.surfarray.pixels3d(green_filtered)
            filtered_alpha = pygame.surfarray.pixels_alpha(green_filtered)
            
            for y in range(new_height):
                for x in range(new_width):
                    # Solo procesar píxeles dentro de la máscara circular y con alpha
                    if mask_array[x, y] > 0 and alpha_array[x, y] > 0:
                        r, g, b = pixel_array[x, y]
                        # Aplicar filtro verde manteniendo la luminosidad
                        # Mezclar hacia verde con saturación
                        green_factor = 0.8  # Factor de verde
                        saturation = 1.3   # Factor de saturación
                        
                        # Calcular nuevo color verde saturado
                        new_r = int(r * (1 - green_factor) + 50 * green_factor)
                        new_g = int(min(255, g * saturation * green_factor + 200 * green_factor))
                        new_b = int(b * (1 - green_factor) + 50 * green_factor)
                        
                        filtered_pixels[x, y] = (new_r, new_g, new_b)
                        filtered_alpha[x, y] = alpha_array[x, y]  # Preservar alpha original
                    else:
                        # Fuera de la máscara o transparente
                        filtered_alpha[x, y] = 0
            
            del pixel_array
            del alpha_array
            del mask_array
            del filtered_pixels
            del filtered_alpha
            
            self.snake_body_image = green_filtered
        except Exception as e:
            print(f"Error al cargar imagen bonificacion.png para cuerpo: {e}")
            self.snake_body_image = None

        # Inicializamos mundo pero arrancamos en presentación
        self.start_new_game()

    # ----------------- SETUP MUNDO -----------------

    def _create_hexagon(self, radius):
        """Crea vértices de un hex regular centrado en (0,0)."""
        vertices = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def _compute_edges(self, vertices):
        """
        Para cada lado del hex: devuelve (v0, normal_salida).
        La normal apunta HACIA FUERA del polígono.
        """
        edges = []
        center = (0.0, 0.0)
        n_vertices = len(vertices)

        for i in range(n_vertices):
            v0 = vertices[i]
            v1 = vertices[(i + 1) % n_vertices]

            ex = v1[0] - v0[0]
            ey = v1[1] - v0[1]

            # Candidata a normal
            nx = ey
            ny = -ex
            length = math.hypot(nx, ny)
            if length == 0:
                continue
            nx /= length
            ny /= length

            # Asegurar que el centro está del lado interior (dist <= 0)
            dist_center = (center[0] - v0[0]) * nx + (center[1] - v0[1]) * ny
            if dist_center > 0:
                nx = -nx
                ny = -ny

            edges.append((v0, [nx, ny]))

        return edges

    def start_new_game(self):
        """Resetea partida (pero no toca el estado/menu)."""
        # actualiza best_score si venimos de una partida jugada
        old_best = self.best_score
        self.best_score = max(self.best_score, self.score)
        # Guardar si se superó el mejor score
        if self.best_score > old_best:
            save_best_score(self.best_score)

        self.score = 0
        self.hex_angle = 0.0

        self.snake_head_pos = [0.0, 0.0]
        self.snake_velocity = [SNAKE_SPEED, 0.0]
        self.last_head_pos = [0.0, 0.0]
        self.next_direction = None
        # Inicializar con algunos segmentos iniciales
        self.snake_body = []
        for i in range(INITIAL_SEGMENTS):
            offset = -(i + 1) * SEGMENT_SPACING
            self.snake_body.append([offset, 0.0])
        
        # Inicializar path de la serpiente
        self.snake_path = []
        # Agregar posiciones iniciales al path
        for i in range(INITIAL_SEGMENTS + 1):
            offset = -i * SEGMENT_SPACING
            self.snake_path.append([offset, 0.0])

        self.rewards = []
        self.game_over_reason = ""
        
        # Limpiar partículas al iniciar nuevo juego
        self.particles = []
        
        # Reinicializar puntos naranjas dentro del hexágono
        self.hex_noise_points = []
        for _ in range(HEX_NOISE_POINTS):
            while True:
                x = random.uniform(-HEX_RADIUS * 0.9, HEX_RADIUS * 0.9)
                y = random.uniform(-HEX_RADIUS * 0.9, HEX_RADIUS * 0.9)
                if self._is_inside_hex([x, y], 0):
                    brightness = random.randint(150, 255)
                    self.hex_noise_points.append({
                        "x": x,
                        "y": y,
                        "size": random.uniform(1.0, 2.0),
                        "brightness": brightness
                    })
                    break

        for _ in range(NUM_REWARDS):
            self.rewards.append(self._create_reward())

    def _init_background(self):
        """Inicializa estrellas y formas de fondo."""
        # Crear estrellas aleatorias
        self.stars = []
        for _ in range(NUM_STARS):
            x = random.uniform(-SCREEN_WIDTH * 1.5, SCREEN_WIDTH * 1.5)
            y = random.uniform(-SCREEN_HEIGHT * 1.5, SCREEN_HEIGHT * 1.5)
            size = random.uniform(1.0, 2.5)
            brightness = random.randint(150, 255)
            self.stars.append({
                "x": x,
                "y": y,
                "size": size,
                "brightness": brightness
            })
        
        # Crear formas de fondo lentas
        self.background_shapes = []
        for _ in range(NUM_BACKGROUND_SHAPES):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(HEX_RADIUS * 1.5, HEX_RADIUS * 3.0)
            x = math.cos(angle) * dist
            y = math.sin(angle) * dist
            size = random.uniform(15, 35)
            speed = random.uniform(5.0, 15.0)
            rotation_speed = random.uniform(-10.0, 10.0)
            self.background_shapes.append({
                "x": x,
                "y": y,
                "size": size,
                "angle": angle,
                "speed": speed,
                "rotation": 0.0,
                "rotation_speed": rotation_speed,
                "color": (
                    random.randint(40, 80),
                    random.randint(50, 90),
                    random.randint(80, 120),
                    40  # Muy tenue
                )
            })
        
        # Crear puntos naranjas dentro del hexágono (ruido/estrellas)
        self.hex_noise_points = []
        for _ in range(HEX_NOISE_POINTS):
            while True:
                x = random.uniform(-HEX_RADIUS * 0.9, HEX_RADIUS * 0.9)
                y = random.uniform(-HEX_RADIUS * 0.9, HEX_RADIUS * 0.9)
                if self._is_inside_hex([x, y], 0):
                    brightness = random.randint(150, 255)
                    self.hex_noise_points.append({
                        "x": x,
                        "y": y,
                        "size": random.uniform(1.0, 2.0),
                        "brightness": brightness
                    })
                    break

    # ----------------- PARTÍCULAS -----------------

    def _create_sparks(self, pos, count=SPARKS_PER_REWARD):
        """Crea chispas en la posición dada cuando se recoge una recompensa."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(SPARK_SPEED_MIN, SPARK_SPEED_MAX)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Color amarillo/dorado para las chispas
            color_brightness = random.randint(200, 255)
            self.particles.append({
                "type": "spark",
                "pos": [pos[0], pos[1]],
                "vel": [vel_x, vel_y],
                "size": random.uniform(SPARK_SIZE * 0.7, SPARK_SIZE * 1.3),
                "color": (color_brightness, color_brightness, random.randint(100, 200), 255),
                "lifetime": PARTICLE_LIFETIME,
                "age": 0.0
            })

    def _create_bounce_flash(self, pos, normal):
        """Crea un flash en el punto de impacto cuando rebota contra la pared."""
        nx, ny = normal
        # Crear flash radial desde el punto de impacto
        self.particles.append({
            "type": "flash",
            "pos": [pos[0], pos[1]],
            "normal": [nx, ny],  # Dirección de la normal para el flash radial
            "size": FLASH_SIZE,
            "color": (255, 255, 200, 255),  # Color blanco/amarillo brillante
            "lifetime": FLASH_LIFETIME,
            "age": 0.0
        })

    def _update_particles(self, delta_time):
        """Actualiza todas las partículas activas."""
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            particle["age"] += delta_time
            
            # Calcular alpha basado en la edad
            life_ratio = particle["age"] / particle["lifetime"]
            if life_ratio >= 1.0:
                particles_to_remove.append(i)
                continue
            
            alpha = int(255 * (1.0 - life_ratio))
            
            if particle["type"] == "spark":
                # Mover chispa
                particle["pos"][0] += particle["vel"][0] * delta_time
                particle["pos"][1] += particle["vel"][1] * delta_time
                # Aplicar fricción ligera
                particle["vel"][0] *= 0.98
                particle["vel"][1] *= 0.98
                # Actualizar color con alpha
                particle["color"] = (
                    particle["color"][0],
                    particle["color"][1],
                    particle["color"][2],
                    alpha
                )
            elif particle["type"] == "flash":
                # El flash solo cambia de tamaño y alpha
                particle["color"] = (
                    particle["color"][0],
                    particle["color"][1],
                    particle["color"][2],
                    alpha
                )
        
        # Eliminar partículas expiradas (de atrás hacia adelante para mantener índices)
        for i in reversed(particles_to_remove):
            self.particles.pop(i)

    def _draw_particles(self):
        """Dibuja todas las partículas activas."""
        for particle in self.particles:
            if particle["type"] == "spark":
                # Dibujar chispa como círculo
                sx, sy = self.world_to_screen(particle["pos"][0], particle["pos"][1])
                color = particle["color"][:3]  # Solo RGB para pygame
                pygame.draw.circle(self.screen, color, (int(sx), int(sy)), int(particle["size"]))
            elif particle["type"] == "flash":
                # Dibujar flash como círculo radial o líneas
                sx, sy = self.world_to_screen(particle["pos"][0], particle["pos"][1])
                nx, ny = particle["normal"]
                
                # Dibujar círculo brillante
                life_ratio = particle["age"] / particle["lifetime"]
                current_size = particle["size"] * (1.0 - life_ratio * 0.5)
                color = particle["color"][:3]
                pygame.draw.circle(self.screen, color, (int(sx), int(sy)), int(current_size))
                
                # Dibujar líneas radiales para efecto de flash
                num_rays = 8
                ray_length = current_size * 1.5
                for i in range(num_rays):
                    angle = (2 * math.pi * i / num_rays) + particle["age"] * 2.0
                    end_x = sx + math.cos(angle) * ray_length
                    end_y = sy + math.sin(angle) * ray_length
                    pygame.draw.line(
                        self.screen,
                        color,
                        (int(sx), int(sy)),
                        (int(end_x), int(end_y)),
                        2
                    )

    # ----------------- GEOMETRÍA / COLISIONES -----------------

    def _is_inside_hex(self, pos, radius=0.0):
        px, py = pos
        for v0, n in self.hex_edges:
            nx, ny = n
            dist = (px - v0[0]) * nx + (py - v0[1]) * ny
            if dist + radius > 0:
                return False
        return True

    def _handle_collision(self, pos, vel, radius, bounce_factor=1.0, create_flash=False):
        """Colisión círculo–hexágono. Devuelve (pos_corregida, vel_reflejada)."""
        px, py = pos
        max_penetration = 0.0
        collision_normal = None
        collision_point = None

        for v0, n in self.hex_edges:
            nx, ny = n
            dist = (px - v0[0]) * nx + (py - v0[1]) * ny
            penetration = dist + radius

            if penetration > max_penetration:
                max_penetration = penetration
                collision_normal = n
                # Calcular punto de impacto aproximado
                collision_point = [px - nx * radius, py - ny * radius]

        if collision_normal is not None and max_penetration > 0.0:
            nx, ny = collision_normal

            # Reposicionar dentro
            px -= nx * max_penetration
            py -= ny * max_penetration
            pos = [px, py]

            # Reflejar velocidad
            old_vel = vel.copy()
            vel = vec_reflect(vel, collision_normal)
            vel = vec_scale(vel, bounce_factor)
            
            # Crear flash si hay rebote significativo y se solicita
            if create_flash and vec_length(old_vel) > 50.0:
                self._create_bounce_flash(collision_point, collision_normal)

        return pos, vel

    def _create_reward(self):
        """Crea una recompensa en posición aleatoria dentro del hex."""
        max_attempts = 50
        attempts = 0
        
        while attempts < max_attempts:
            x = random.uniform(-HEX_RADIUS * 0.75, HEX_RADIUS * 0.75)
            y = random.uniform(-HEX_RADIUS * 0.75, HEX_RADIUS * 0.75)
            pos = [x, y]
            
            # Verificar que esté dentro del hexágono
            if self._is_inside_hex(pos, REWARD_RADIUS + 2):
                # Evitar spawn justo encima de la cabeza o del cuerpo
                dx = pos[0] - self.snake_head_pos[0]
                dy = pos[1] - self.snake_head_pos[1]
                dist_to_head = dx * dx + dy * dy
                
                # Verificar distancia mínima a la cabeza
                if dist_to_head > (SNAKE_RADIUS + 50) ** 2:
                    # Verificar distancia mínima a los segmentos del cuerpo
                    too_close = False
                    for segment in self.snake_body:
                        dx_seg = pos[0] - segment[0]
                        dy_seg = pos[1] - segment[1]
                        if dx_seg * dx_seg + dy_seg * dy_seg < (SNAKE_RADIUS + 30) ** 2:
                            too_close = True
                            break
                    
                    if not too_close:
                        # Crear velocidad inicial aleatoria
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(60.0, 120.0)
                        vel = [math.cos(angle) * speed, math.sin(angle) * speed]
                        return {"pos": pos, "vel": vel}
            
            attempts += 1
        
        # Si no se encontró posición válida después de muchos intentos,
        # usar una posición segura lejos del centro
        angle_pos = random.uniform(0, 2 * math.pi)
        dist_from_center = random.uniform(HEX_RADIUS * 0.3, HEX_RADIUS * 0.6)
        pos = [math.cos(angle_pos) * dist_from_center, math.sin(angle_pos) * dist_from_center]
        
        # Verificar que esté dentro
        if not self._is_inside_hex(pos, REWARD_RADIUS):
            # Ajustar hacia adentro si está fuera
            for _ in range(10):
                pos[0] *= 0.9
                pos[1] *= 0.9
                if self._is_inside_hex(pos, REWARD_RADIUS):
                    break
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60.0, 120.0)
        vel = [math.cos(angle) * speed, math.sin(angle) * speed]
        
        return {"pos": pos, "vel": vel}

    # ----------------- COORDENADAS -----------------

    def world_to_screen(self, x, y):
        """
        Coord. locales (hex) -> pantalla, aplicando rotación del escenario.
        Física siempre en coords locales, solo la vista gira.
        """
        angle_rad = math.radians(self.hex_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        sx = self.cx + x * cos_a - y * sin_a
        sy = self.cy + x * sin_a + y * cos_a
        return sx, sy

    # ----------------- INPUT -----------------

    def _set_direction(self, screen_direction):
        """
        Establece la dirección deseada de la serpiente (Snake clásico).
        screen_direction es en coordenadas de pantalla (arriba = +Y).
        La dirección cambia inmediatamente si no es opuesta a la actual.
        """
        # Normalizar el vector de dirección de pantalla
        length = vec_length(screen_direction)
        if length == 0:
            return
        
        # Convertir dirección de pantalla a coordenadas locales del hexágono
        angle_rad = math.radians(-self.hex_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Rotar el vector de dirección de pantalla a coordenadas locales
        local_x = screen_direction[0] * cos_a - screen_direction[1] * sin_a
        local_y = screen_direction[0] * sin_a + screen_direction[1] * cos_a
        
        # Normalizar
        local_length = math.hypot(local_x, local_y)
        if local_length > 0:
            local_x /= local_length
            local_y /= local_length
        
        # Obtener dirección actual normalizada
        current_vel = self.snake_velocity
        speed = vec_length(current_vel)
        if speed == 0:
            speed = SNAKE_SPEED
        
        current_dir_x = current_vel[0] / speed if speed > 0 else 1.0
        current_dir_y = current_vel[1] / speed if speed > 0 else 0.0
        
        # Verificar si la dirección es opuesta (producto punto negativo)
        dot_product = current_dir_x * local_x + current_dir_y * local_y
        if dot_product < -0.5:  # Dirección opuesta (no permitir)
            return
        
        # Cambiar dirección inmediatamente (Snake clásico)
        self.snake_velocity = [local_x * speed, local_y * speed]
        self.next_direction = None  # Limpiar dirección pendiente

    def _handle_key_press(self, key):
        """Maneja eventos de teclado."""
        # Pantalla de presentación - iniciar juego directamente
        if self.state == STATE_PRESENTATION:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_new_game()
                self.state = STATE_PLAYING
            return
        
        # Menú inicial
        if self.state == STATE_MENU:
            if key in (
                pygame.K_RETURN,
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
            ):
                self.start_new_game()
                self.state = STATE_PLAYING
            return

        # Game over
        if self.state == STATE_GAME_OVER:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                self.state = STATE_PRESENTATION  # Volver a pantalla de presentación
            return

        # Juego en marcha - controles direccionales clásicos
        if self.state == STATE_PLAYING:
            # Arriba: W o flecha arriba (invertir Y porque en pygame Y positivo es hacia abajo)
            if key in (pygame.K_w, pygame.K_UP):
                self._set_direction([0.0, -1.0])
            # Abajo: S o flecha abajo
            elif key in (pygame.K_s, pygame.K_DOWN):
                self._set_direction([0.0, 1.0])
            # Izquierda: A o flecha izquierda
            elif key in (pygame.K_a, pygame.K_LEFT):
                self._set_direction([-1.0, 0.0])
            # Derecha: D o flecha derecha
            elif key in (pygame.K_d, pygame.K_RIGHT):
                self._set_direction([1.0, 0.0])

    def _point_in_rect(self, x, y, rect):
        """Verifica si un punto (x, y) está dentro de un rectángulo.
        rect es (left, top, width, height) donde top es la coordenada Y superior.
        """
        left, top, width, height = rect
        return left <= x <= left + width and top <= y <= top + height

    def _handle_mouse_press(self, x, y, button):
        """Maneja eventos de mouse."""
        # pygame ya da coordenadas con Y=0 arriba, no necesitamos invertir
        
        if self.state == STATE_PRESENTATION:
            # Verificar clic en botón PLAY - iniciar juego directamente
            if self._point_in_rect(x, y, self.play_button_rect):
                self.start_new_game()
                self.state = STATE_PLAYING
        elif self.state == STATE_MENU:
            self.start_new_game()
            self.state = STATE_PLAYING
        elif self.state == STATE_GAME_OVER:
            if self._point_in_rect(x, y, self.restart_button_rect):
                self.state = STATE_PRESENTATION  # Volver a pantalla de presentación

    # ----------------- UPDATE -----------------

    def _update_snake(self, delta_time):
        # Guardar posición anterior de la cabeza
        self.last_head_pos = self.snake_head_pos.copy()
        
        # Mover cabeza
        self.snake_head_pos[0] += self.snake_velocity[0] * delta_time
        self.snake_head_pos[1] += self.snake_velocity[1] * delta_time

        # Rebote con paredes (con flash de impacto)
        self.snake_head_pos, self.snake_velocity = self._handle_collision(
            self.snake_head_pos, self.snake_velocity, SNAKE_RADIUS, bounce_factor=1.0, create_flash=True
        )

        # Agregar posición actual al path (solo si se movió suficiente distancia)
        if len(self.snake_path) == 0:
            self.snake_path.append(self.snake_head_pos.copy())
        else:
            last_path_pos = self.snake_path[-1]
            dx = self.snake_head_pos[0] - last_path_pos[0]
            dy = self.snake_head_pos[1] - last_path_pos[1]
            dist = math.hypot(dx, dy)
            
            # Agregar punto al path cada vez que avance la distancia de espaciado
            if dist >= SEGMENT_SPACING * 0.8:
                self.snake_path.append(self.snake_head_pos.copy())
                # Mantener solo los puntos necesarios (uno por segmento + algunos extras)
                max_path_length = len(self.snake_body) + 5
                if len(self.snake_path) > max_path_length:
                    self.snake_path.pop(0)

        # Mover segmentos del cuerpo siguiendo el path exacto (Snake clásico)
        if len(self.snake_body) > 0 and len(self.snake_path) > 1:
            # Cada segmento sigue un punto específico del path
            for i, segment in enumerate(self.snake_body):
                # Índice en el path para este segmento (desde el final hacia atrás)
                path_index = len(self.snake_path) - 2 - i
                if path_index >= 0 and path_index < len(self.snake_path):
                    # El segmento va directamente a su posición en el path
                    target_pos = self.snake_path[path_index]
                    segment[0] = target_pos[0]
                    segment[1] = target_pos[1]
                elif path_index < 0:
                    # Si no hay suficientes puntos en el path, calcular posición detrás del anterior
                    if i == 0:
                        # Primer segmento sigue a la cabeza
                        dx = self.snake_head_pos[0] - segment[0]
                        dy = self.snake_head_pos[1] - segment[1]
                        dist = math.hypot(dx, dy)
                        if dist > SEGMENT_SPACING:
                            if dist > 0:
                                dx /= dist
                                dy /= dist
                            segment[0] = self.snake_head_pos[0] - dx * SEGMENT_SPACING
                            segment[1] = self.snake_head_pos[1] - dy * SEGMENT_SPACING
                    else:
                        # Otros segmentos siguen al anterior
                        prev_seg = self.snake_body[i - 1]
                        dx = prev_seg[0] - segment[0]
                        dy = prev_seg[1] - segment[1]
                        dist = math.hypot(dx, dy)
                        if dist > SEGMENT_SPACING:
                            if dist > 0:
                                dx /= dist
                                dy /= dist
                            segment[0] = prev_seg[0] - dx * SEGMENT_SPACING
                            segment[1] = prev_seg[1] - dy * SEGMENT_SPACING

    def _update_rewards(self, delta_time):
        for reward in self.rewards:
            # Gravedad en coordenadas locales (hacia abajo en Y negativo)
            reward["vel"][1] += GRAVITY * delta_time

            # Movimiento
            reward["pos"][0] += reward["vel"][0] * delta_time
            reward["pos"][1] += reward["vel"][1] * delta_time

            # Verificar y manejar colisión con las paredes del hexágono
            # Esto reposiciona y refleja la velocidad correctamente
            reward["pos"], reward["vel"] = self._handle_collision(
                reward["pos"], reward["vel"], REWARD_RADIUS, bounce_factor=REWARD_BOUNCE
            )
            
            # Asegurar que siempre esté dentro del hexágono (sin reposicionar en centro)
            # Si se sale, usar la función de colisión múltiples veces para empujarla dentro
            max_iterations = 5
            iteration = 0
            while not self._is_inside_hex(reward["pos"], REWARD_RADIUS) and iteration < max_iterations:
                reward["pos"], reward["vel"] = self._handle_collision(
                    reward["pos"], reward["vel"], REWARD_RADIUS, bounce_factor=0.5
                )
                iteration += 1
            
            # Si aún está fuera después de intentos, reposicionarla aleatoriamente dentro del hexágono
            if not self._is_inside_hex(reward["pos"], REWARD_RADIUS):
                # Buscar posición aleatoria válida dentro del hexágono
                attempts = 0
                while attempts < 20:
                    x = random.uniform(-HEX_RADIUS * 0.7, HEX_RADIUS * 0.7)
                    y = random.uniform(-HEX_RADIUS * 0.7, HEX_RADIUS * 0.7)
                    new_pos = [x, y]
                    if self._is_inside_hex(new_pos, REWARD_RADIUS):
                        reward["pos"] = new_pos
                        # Dar velocidad aleatoria
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(60.0, 100.0)
                        reward["vel"] = [math.cos(angle) * speed, math.sin(angle) * speed]
                        break
                    attempts += 1

    def _check_reward_collisions(self):
        head = self.snake_head_pos
        eaten = []

        for reward in self.rewards:
            dx = head[0] - reward["pos"][0]
            dy = head[1] - reward["pos"][1]
            if dx * dx + dy * dy <= (SNAKE_RADIUS + REWARD_RADIUS) ** 2:
                eaten.append(reward)
                self.score += 1
                # Crear chispas cuando se come una recompensa
                self._create_sparks(reward["pos"])
                # Agregar nuevos segmentos cuando se come comida
                for _ in range(SEGMENTS_PER_FOOD):
                    if len(self.snake_body) > 0:
                        # Agregar al final usando el path o la dirección del último segmento
                        last_seg = self.snake_body[-1]
                        
                        # Intentar usar el path si está disponible
                        if len(self.snake_path) > len(self.snake_body):
                            # Usar posición del path correspondiente
                            path_idx = len(self.snake_path) - len(self.snake_body) - 1
                            if path_idx >= 0:
                                new_seg = self.snake_path[path_idx].copy()
                            else:
                                # Calcular desde el último segmento
                                speed = vec_length(self.snake_velocity)
                                if speed > 0:
                                    dx_dir = -self.snake_velocity[0] / speed
                                    dy_dir = -self.snake_velocity[1] / speed
                                else:
                                    dx_dir = -1.0
                                    dy_dir = 0.0
                                new_seg = [
                                    last_seg[0] + dx_dir * SEGMENT_SPACING,
                                    last_seg[1] + dy_dir * SEGMENT_SPACING
                                ]
                        else:
                            # Calcular dirección hacia atrás desde el último segmento
                            if len(self.snake_body) > 1:
                                prev_seg = self.snake_body[-2]
                                dx_seg = last_seg[0] - prev_seg[0]
                                dy_seg = last_seg[1] - prev_seg[1]
                            else:
                                dx_seg = last_seg[0] - self.snake_head_pos[0]
                                dy_seg = last_seg[1] - self.snake_head_pos[1]
                            
                            dist_seg = math.hypot(dx_seg, dy_seg)
                            if dist_seg > 0:
                                dx_seg /= dist_seg
                                dy_seg /= dist_seg
                            else:
                                speed = vec_length(self.snake_velocity)
                                if speed > 0:
                                    dx_seg = -self.snake_velocity[0] / speed
                                    dy_seg = -self.snake_velocity[1] / speed
                                else:
                                    dx_seg = -1.0
                                    dy_seg = 0.0
                            
                            new_seg = [
                                last_seg[0] + dx_seg * SEGMENT_SPACING,
                                last_seg[1] + dy_seg * SEGMENT_SPACING
                            ]
                        self.snake_body.append(new_seg)
                    else:
                        # Si no hay segmentos, agregar detrás de la cabeza usando el path
                        if len(self.snake_path) > 0:
                            new_seg = self.snake_path[0].copy()
                        else:
                            speed = vec_length(self.snake_velocity)
                            if speed > 0:
                                dx_dir = -self.snake_velocity[0] / speed
                                dy_dir = -self.snake_velocity[1] / speed
                            else:
                                dx_dir = -1.0
                                dy_dir = 0.0
                            new_seg = [
                                self.snake_head_pos[0] + dx_dir * SEGMENT_SPACING,
                                self.snake_head_pos[1] + dy_dir * SEGMENT_SPACING
                            ]
                        self.snake_body.append(new_seg)

        for r in eaten:
            self.rewards.remove(r)

        # Mantener siempre NUM_REWARDS recompensas
        while len(self.rewards) < NUM_REWARDS:
            self.rewards.append(self._create_reward())

    def _set_game_over(self, reason: str):
        self.state = STATE_GAME_OVER
        self.game_over_reason = reason
        old_best = self.best_score
        self.best_score = max(self.best_score, self.score)
        # Guardar si se superó el mejor score
        if self.best_score > old_best:
            save_best_score(self.best_score)

    def _check_self_collision(self):
        """Si la cabeza toca el cuerpo => game over."""
        head = self.snake_head_pos
        radius2 = (SNAKE_RADIUS * 1.5) ** 2  # Radio de colisión

        for segment in self.snake_body:
            dx = head[0] - segment[0]
            dy = head[1] - segment[1]
            if dx * dx + dy * dy < radius2:
                self._set_game_over("Te has chocado con tu propio cuerpo.")
                return

    def update(self, delta_time: float):
        # el hexágono rota siempre (visual) con velocidad variable
        # Actualizar temporizador para cambios aleatorios
        self.hex_rotation_timer += delta_time
        
        # Cambiar velocidad/dirección de rotación aleatoriamente
        if self.hex_rotation_timer >= self.hex_rotation_change_time:
            # Cambiar a nueva velocidad aleatoria (puede ser positiva o negativa)
            speed_range = HEX_ROTATION_SPEED_MAX - HEX_ROTATION_SPEED_MIN
            random_speed = HEX_ROTATION_SPEED_MIN + random.random() * speed_range
            # 50% de probabilidad de rotar en sentido contrario
            if random.random() < 0.5:
                random_speed = -random_speed
            
            self.hex_rotation_speed = random_speed
            self.hex_rotation_timer = 0.0
            # Programar próximo cambio aleatorio
            self.hex_rotation_change_time = random.uniform(HEX_ROTATION_CHANGE_MIN, HEX_ROTATION_CHANGE_MAX)
        
        # Aplicar rotación con velocidad actual
        self.hex_angle = (self.hex_angle + self.hex_rotation_speed * delta_time) % 360.0

        # Actualizar formas de fondo (rotación lenta)
        for shape in self.background_shapes:
            shape["rotation"] += shape["rotation_speed"] * delta_time * math.pi / 180.0
            # Mover formas lentamente en círculo alrededor del centro
            shape["angle"] += shape["speed"] * delta_time * 0.001
            dist = math.hypot(shape["x"], shape["y"])
            shape["x"] = math.cos(shape["angle"]) * dist
            shape["y"] = math.sin(shape["angle"]) * dist

        if self.state != STATE_PLAYING:
            return

        self._update_snake(delta_time)
        self._update_rewards(delta_time)
        self._check_reward_collisions()
        self._check_self_collision()
        self._update_particles(delta_time)

    # ----------------- DIBUJO -----------------

    def _draw_background(self):
        """Capa BACK: fondo, estrellas, grid, formas lentas con parallax."""
        # Calcular offset de parallax basado en la posición de la serpiente
        parallax_x = self.snake_head_pos[0] * PARALLAX_FACTOR
        parallax_y = self.snake_head_pos[1] * PARALLAX_FACTOR
        
        # Dibujar grid con parallax
        # El grid se mueve según la posición de la serpiente
        grid_start_x = self.cx + parallax_x
        grid_start_y = self.cy + parallax_y
        
        # Calcular el offset del grid para que se alinee correctamente
        grid_offset_x = grid_start_x % GRID_SPACING
        grid_offset_y = grid_start_y % GRID_SPACING
        
        # Líneas verticales del grid
        start_x = -grid_offset_x
        for x in range(int(start_x), int(SCREEN_WIDTH + GRID_SPACING), GRID_SPACING):
            if 0 <= x <= SCREEN_WIDTH:
                color = GRID_COLOR[:3]  # Solo RGB
                pygame.draw.line(
                    self.screen,
                    color,
                    (x, 0),
                    (x, SCREEN_HEIGHT),
                    1
                )
        
        # Líneas horizontales del grid
        start_y = -grid_offset_y
        for y in range(int(start_y), int(SCREEN_HEIGHT + GRID_SPACING), GRID_SPACING):
            if 0 <= y <= SCREEN_HEIGHT:
                color = GRID_COLOR[:3]  # Solo RGB
                pygame.draw.line(
                    self.screen,
                    color,
                    (0, y),
                    (SCREEN_WIDTH, y),
                    1
                )
        
        # Dibujar estrellas con parallax
        for star in self.stars:
            # Aplicar parallax a las estrellas
            star_x = self.cx + star["x"] + parallax_x
            star_y = self.cy + star["y"] + parallax_y
            
            # Solo dibujar si está en pantalla (con margen)
            if -50 <= star_x <= SCREEN_WIDTH + 50 and -50 <= star_y <= SCREEN_HEIGHT + 50:
                color = (
                    star["brightness"],
                    star["brightness"],
                    star["brightness"]
                )
                pygame.draw.circle(self.screen, color, (int(star_x), int(star_y)), int(star["size"]))
        
        # Dibujar cruces grandes tenues con parallax (como en la imagen)
        for shape in self.background_shapes:
            # Aplicar parallax a las formas
            shape_x = self.cx + shape["x"] + parallax_x
            shape_y = self.cy + shape["y"] + parallax_y
            
            # Solo dibujar si está cerca de la pantalla
            if -shape["size"] * 2 <= shape_x <= SCREEN_WIDTH + shape["size"] * 2:
                if -shape["size"] * 2 <= shape_y <= SCREEN_HEIGHT + shape["size"] * 2:
                    # Dibujar cruz grande tenue
                    cross_size = shape["size"]
                    cross_color = (shape["color"][0], shape["color"][1], shape["color"][2])  # Solo RGB
                    # Línea horizontal
                    pygame.draw.line(
                        self.screen,
                        cross_color,
                        (int(shape_x - cross_size), int(shape_y)),
                        (int(shape_x + cross_size), int(shape_y)),
                        2
                    )
                    # Línea vertical
                    pygame.draw.line(
                        self.screen,
                        cross_color,
                        (int(shape_x), int(shape_y - cross_size)),
                        (int(shape_x), int(shape_y + cross_size)),
                        2
                    )

    def _draw_mid(self):
        """Capa MID: hexágono + rewards con glow y sombras."""
        # Dibujar sombras primero (debajo de todo)
        self._draw_shadows()
        # Dibujar hexágono
        self._draw_hexagon()
        # Dibujar recompensas
        self._draw_rewards()

    def _draw_front(self):
        """Capa FRONT: snake + luces dinámicas + HUD + partículas."""
        # Dibujar sombras de la serpiente
        self._draw_snake_shadows()
        # Dibujar serpiente
        self._draw_snake()
        # Partículas sobre la serpiente pero bajo el HUD
        self._draw_particles()
        # HUD siempre al frente
        self._draw_hud()

    def _draw_hexagon(self):
        points = [self.world_to_screen(x, y) for (x, y) in self.hex_vertices_local]
        # Convertir a enteros para pygame
        int_points = [(int(px), int(py)) for px, py in points]
        # Relleno azul oscuro como en la imagen
        pygame.draw.polygon(self.screen, (20, 30, 50), int_points)
        # Borde azul claro pixelado
        pygame.draw.polygon(self.screen, (100, 150, 255), int_points, 3)

    def _draw_snake(self):
        # Dibujar cuerpo usando bonificacion.png con filtro verde
        if self.snake_body_image:
            for idx, segment in enumerate(self.snake_body):
                sx, sy = self.world_to_screen(segment[0], segment[1])
                img_width, img_height = self.snake_body_image.get_size()
                # Centrar la imagen en la posición del segmento
                img_x = int(sx - img_width / 2)
                img_y = int(sy - img_height / 2)
                self.screen.blit(self.snake_body_image, (img_x, img_y))
        else:
            # Fallback: círculos verdes si no se puede cargar la imagen
            for idx, segment in enumerate(self.snake_body):
                sx, sy = self.world_to_screen(segment[0], segment[1])
                radius = SNAKE_RADIUS
                pygame.draw.circle(self.screen, (50, 150, 50), (int(sx), int(sy)), int(radius))
                pygame.draw.circle(self.screen, (30, 100, 30), (int(sx), int(sy)), int(radius), 1)

        # Dibujar cabeza (círculo verde sin ojos)
        hx, hy = self.world_to_screen(self.snake_head_pos[0], self.snake_head_pos[1])
        # Cabeza verde más clara
        pygame.draw.circle(self.screen, (100, 200, 100), (int(hx), int(hy)), int(SNAKE_RADIUS + 2))
        pygame.draw.circle(self.screen, (70, 180, 70), (int(hx), int(hy)), int(SNAKE_RADIUS))

    def _draw_rewards(self):
        for reward in self.rewards:
            sx, sy = self.world_to_screen(reward["pos"][0], reward["pos"][1])
            # Dibujar imagen de bonificación si está disponible
            if self.bonus_image:
                img_width, img_height = self.bonus_image.get_size()
                # Centrar la imagen en la posición de la recompensa
                img_x = int(sx - img_width / 2)
                img_y = int(sy - img_height / 2)
                self.screen.blit(self.bonus_image, (img_x, img_y))
            else:
                # Fallback: círculos rojos si no se puede cargar la imagen
                radius = REWARD_RADIUS
                pygame.draw.circle(self.screen, (255, 50, 50), (int(sx), int(sy)), int(radius))
                pygame.draw.circle(self.screen, (200, 20, 20), (int(sx), int(sy)), int(radius), 1)
    
    def _draw_shadows(self):
        """Dibuja sombras proyectadas por el hexágono y recompensas."""
        # Crear superficie temporal para sombras con alpha
        shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Sombra del hexágono
        points = [self.world_to_screen(x, y) for (x, y) in self.hex_vertices_local]
        shadow_points = [(px + SHADOW_OFFSET_X, py + SHADOW_OFFSET_Y) for px, py in points]
        int_shadow_points = [(int(px), int(py)) for px, py in shadow_points]
        
        # Dibujar sombra del hexágono
        shadow_color = (0, 0, 0, SHADOW_ALPHA)
        pygame.draw.polygon(shadow_surface, shadow_color, int_shadow_points)
        
        # Sombras de las recompensas
        for reward in self.rewards:
            sx, sy = self.world_to_screen(reward["pos"][0], reward["pos"][1])
            shadow_x = sx + SHADOW_OFFSET_X
            shadow_y = sy + SHADOW_OFFSET_Y
            
            # Sombra elíptica (más ancha que alta) - usar círculo ligeramente achatado
            pygame.draw.circle(shadow_surface, shadow_color, (int(shadow_x), int(shadow_y)), int(REWARD_RADIUS * 1.2))
        
        # Dibujar superficie de sombras en la pantalla principal
        self.screen.blit(shadow_surface, (0, 0))
    
    def _draw_snake_shadows(self):
        """Dibuja sombras proyectadas por la serpiente."""
        if self.state != STATE_PLAYING:
            return
        
        # Crear superficie temporal para sombras con alpha
        shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Si estamos usando imagen para el cuerpo, crear sombra basada en la imagen
        if self.snake_body_image:
            # Sombra del cuerpo de la serpiente usando la imagen
            for segment in self.snake_body:
                sx, sy = self.world_to_screen(segment[0], segment[1])
                shadow_x = sx + SHADOW_OFFSET_X
                shadow_y = sy + SHADOW_OFFSET_Y
                
                img_width, img_height = self.snake_body_image.get_size()
                img_x = int(shadow_x - img_width / 2)
                img_y = int(shadow_y - img_height / 2)
                
                # Crear una copia oscura y semi-transparente de la imagen para la sombra
                shadow_img = self.snake_body_image.copy()
                shadow_img.fill((0, 0, 0, SHADOW_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
                shadow_surface.blit(shadow_img, (img_x, img_y))
        else:
            # Fallback: usar círculos si no hay imagen
            for segment in self.snake_body:
                sx, sy = self.world_to_screen(segment[0], segment[1])
                shadow_x = sx + SHADOW_OFFSET_X
                shadow_y = sy + SHADOW_OFFSET_Y
                
                shadow_color = (0, 0, 0, SHADOW_ALPHA)
                pygame.draw.circle(shadow_surface, shadow_color, (int(shadow_x), int(shadow_y)), int(SNAKE_RADIUS * 0.9))
        
        # Sombra de la cabeza (siempre círculo)
        hx, hy = self.world_to_screen(self.snake_head_pos[0], self.snake_head_pos[1])
        shadow_x = hx + SHADOW_OFFSET_X
        shadow_y = hy + SHADOW_OFFSET_Y
        
        shadow_color = (0, 0, 0, SHADOW_ALPHA)
        pygame.draw.circle(shadow_surface, shadow_color, (int(shadow_x), int(shadow_y)), int(SNAKE_RADIUS * 1.1))
        
        # Dibujar superficie de sombras en la pantalla principal
        self.screen.blit(shadow_surface, (0, 0))

    def _draw_hud(self):
        # HUD optimizado para formato vertical móvil - con más espacio
        pixel_size = 2
        
        # Crear superficie temporal para HUD con transparencia
        hud_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Barra superior con más altura para mejor espaciado
        hud_height = 65
        pygame.draw.rect(
            hud_surface,
            (10, 10, 30, 200),  # Fondo semi-transparente
            (0, SCREEN_HEIGHT - hud_height, SCREEN_WIDTH, hud_height)
        )
        
        # SCORE en la parte superior izquierda - con más espacio
        score_label = "SCORE"
        score_value = f"{self.score:05d}"
        score_x = 15
        score_y_label = 20  # Parte superior (Y pequeño = arriba en pygame)
        score_y_value = 35
        draw_pixel_text(hud_surface, score_label, score_x, score_y_label, COLOR_WHITE, pixel_size)
        draw_pixel_text(hud_surface, score_value, score_x, score_y_value, COLOR_WHITE, pixel_size)

        # BEST en el centro superior - con más espacio
        best_label = "BEST"
        best_value = f"{self.best_score:05d}"
        best_label_width = len(best_label) * 6 * pixel_size
        best_x = SCREEN_WIDTH / 2 - best_label_width / 2
        best_y_label = 20  # Parte superior
        best_y_value = 35
        draw_pixel_text(hud_surface, best_label, best_x, best_y_label, COLOR_LIGHT_GRAY, pixel_size)
        best_value_width = len(best_value) * 6 * pixel_size
        draw_pixel_text(hud_surface, best_value, SCREEN_WIDTH / 2 - best_value_width / 2, best_y_value, COLOR_LIGHT_GRAY, pixel_size)

        # REWARDS en la parte superior derecha - con más espacio
        rewards_label = "REWARDS"
        rewards_value = f"x{len(self.rewards)}"
        rewards_label_width = len(rewards_label) * 6 * pixel_size
        rewards_value_width = len(rewards_value) * 6 * pixel_size
        rewards_x = SCREEN_WIDTH - max(rewards_label_width, rewards_value_width + 8) - 15
        rewards_y_label = 20  # Parte superior
        rewards_y_value = 35
        draw_pixel_text(hud_surface, rewards_label, rewards_x, rewards_y_label, COLOR_LIGHT_GRAY, pixel_size)
        # Icono pequeño rojo junto al valor
        icon_x = rewards_x + rewards_value_width + 4
        icon_y = rewards_y_value + 7  # Ajustar para que esté alineado
        pygame.draw.circle(hud_surface, (255, 50, 50), (int(icon_x), int(icon_y)), 3)
        draw_pixel_text(hud_surface, rewards_value, rewards_x, rewards_y_value, COLOR_LIGHT_GRAY, pixel_size)
        
        # Controles en la parte inferior - con más espacio
        hint_height = 50
        pygame.draw.rect(
            hud_surface,
            (10, 10, 30, 200),  # Fondo semi-transparente
            (0, SCREEN_HEIGHT - hint_height, SCREEN_WIDTH, hint_height)
        )
        controls_text = "← ↑ → MOVE"
        text_width = len(controls_text) * 6 * pixel_size
        draw_pixel_text(hud_surface, controls_text, SCREEN_WIDTH / 2 - text_width / 2, SCREEN_HEIGHT - 25, COLOR_WHITE, pixel_size)
        
        # Dibujar HUD en la pantalla principal
        self.screen.blit(hud_surface, (0, 0))

    def _draw_presentation(self):
        """Dibuja la pantalla de presentación con la imagen de presentación"""
        # Dibujar imagen de fondo (presentación) ajustada a toda la pantalla
        if self.presentation_image:
            # La imagen ya está escalada al tamaño completo de la pantalla
            self.screen.blit(self.presentation_image, (0, 0))
        else:
            # Si no se pudo cargar la imagen, usar fondo de color
            self.screen.fill((15, 10, 25))
        
        # Dibujar botón PLAY centrado en la parte inferior
        bx, by, bw, bh = self.play_button_rect
        pygame.draw.rect(
            self.screen,
            COLOR_AMAZON,
            (int(bx), int(by), int(bw), int(bh))
        )
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            (int(bx), int(by), int(bw), int(bh)),
            2
        )
        
        # Texto "PLAY" en pixel art - centrado vertical y horizontalmente
        play_text = "PLAY"
        pixel_size = 2
        play_width = len(play_text) * 6 * pixel_size
        # Altura del texto: 7 filas en la fuente * pixel_size
        text_height = 7 * pixel_size
        # Centrar verticalmente: centro del botón - mitad de la altura del texto
        text_y = by + bh / 2 - text_height / 2
        # Centrar horizontalmente
        text_x = bx + bw / 2 - play_width / 2
        draw_pixel_text(self.screen, play_text, text_x, text_y, COLOR_WHITE, pixel_size)

    def _draw_menu(self):
        pixel_size = 3  # Tamaño ajustado para móviles
        
        # Título en pixel art - con más espacio (parte superior)
        title = "HEX SNAKE"
        title_width = len(title) * 6 * pixel_size
        draw_pixel_text(self.screen, title, SCREEN_WIDTH / 2 - title_width / 2, SCREEN_HEIGHT * 0.20, (100, 255, 255), pixel_size)

        # Subtítulo (más pequeño y dividido en líneas para móviles) - con más espacio
        subtitle1 = "DENTRO DE UN"
        subtitle2 = "HEXAGONO"
        subtitle1_width = len(subtitle1) * 6 * 2
        subtitle2_width = len(subtitle2) * 6 * 2
        draw_pixel_text(self.screen, subtitle1, SCREEN_WIDTH / 2 - subtitle1_width / 2, SCREEN_HEIGHT * 0.30, COLOR_LIGHT_GRAY, 2)
        draw_pixel_text(self.screen, subtitle2, SCREEN_WIDTH / 2 - subtitle2_width / 2, SCREEN_HEIGHT * 0.35, COLOR_LIGHT_GRAY, 2)

        # Instrucciones - con más espacio desde arriba
        instructions = "TOCA PARA EMPEZAR"
        inst_width = len(instructions) * 6 * 2
        draw_pixel_text(self.screen, instructions, SCREEN_WIDTH / 2 - inst_width / 2, SCREEN_HEIGHT * 0.50, COLOR_WHITE, 2)

    def _draw_game_over_overlay(self):
        # Crear superficie temporal para overlay con transparencia
        overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Panel simplificado: solo GAME OVER y botón de reiniciar
        panel_width = SCREEN_WIDTH - 30
        panel_height = 180  # Más compacto
        panel_left = SCREEN_WIDTH / 2 - panel_width / 2
        panel_bottom = SCREEN_HEIGHT / 2 - panel_height / 2

        pygame.draw.rect(
            overlay_surface,
            (0, 0, 0, 220),
            (int(panel_left), int(panel_bottom), int(panel_width), int(panel_height))
        )
        pygame.draw.rect(
            overlay_surface,
            COLOR_AQUAMARINE,
            (int(panel_left), int(panel_bottom), int(panel_width), int(panel_height)),
            2
        )

        # GAME OVER en pixel art - centrado arriba del panel
        pixel_size = 3
        game_over_text = "GAME OVER"
        text_width = len(game_over_text) * 6 * pixel_size
        # Texto arriba del centro del panel
        game_over_y = panel_bottom + panel_height - 60
        draw_pixel_text(overlay_surface, game_over_text, SCREEN_WIDTH / 2 - text_width / 2, game_over_y, COLOR_WHITE, pixel_size)

        # Botón de reinicio - centrado debajo de GAME OVER
        bx, by, bw, bh = self.restart_button_rect
        # Posicionar botón centrado debajo del texto
        by = game_over_y - 50  # Debajo del texto GAME OVER
        bx = SCREEN_WIDTH / 2 - bw / 2
        self.restart_button_rect = (bx, by, bw, bh)
        
        pygame.draw.rect(
            overlay_surface,
            COLOR_AMAZON,
            (int(bx), int(by), int(bw), int(bh))
        )
        pygame.draw.rect(
            overlay_surface,
            COLOR_WHITE,
            (int(bx), int(by), int(bw), int(bh)),
            2
        )

        # Botón "Reiniciar" en pixel art - centrado vertical y horizontalmente
        restart_text = "REINICIAR"
        pixel_size = 2
        restart_width = len(restart_text) * 6 * pixel_size
        # Altura del texto: 7 filas en la fuente * pixel_size
        text_height = 7 * pixel_size
        # Centrar verticalmente: centro del botón - mitad de la altura del texto
        text_y = by + bh / 2 - text_height / 2
        # Centrar horizontalmente
        text_x = bx + bw / 2 - restart_width / 2
        draw_pixel_text(overlay_surface, restart_text, text_x, text_y, COLOR_WHITE, pixel_size)
        
        # Dibujar overlay en la pantalla principal
        self.screen.blit(overlay_surface, (0, 0))

    def draw(self):
        # Limpiar pantalla
        self.screen.fill(self.bg_color)

        # Pantalla de presentación (solo imagen y botón, sin fondo del juego)
        if self.state == STATE_PRESENTATION:
            self._draw_presentation()
            return

        # Dibujar en orden de capas: BACK -> MID -> FRONT
        self._draw_background()  # BACK: fondo, estrellas, grid, formas lentas
        self._draw_mid()          # MID: hexágono + rewards
        self._draw_front()        # FRONT: snake + HUD

        # Overlays de menú y game over (siempre al frente)
        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over_overlay()

    def run(self):
        """Loop principal del juego."""
        while self.running:
            # Calcular delta_time
            delta_time = self.clock.tick(60) / 1000.0  # Convertir a segundos
            
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_press(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_press(event.pos[0], event.pos[1], event.button)
            
            # Actualizar juego
            self.update(delta_time)
            
            # Dibujar
            self.draw()
            
            # Actualizar pantalla
            pygame.display.flip()
        
        pygame.quit()


# ----------------- MAIN -----------------

def main():
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()

