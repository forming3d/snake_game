# 🐍 Hex Snake Mobile

Un juego clásico de Snake con un giro único: juega dentro de un hexágono rotativo con física realista y efectos visuales impresionantes.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📱 Características

- **Juego de Snake único**: Controla una serpiente dentro de un hexágono rotativo
- **Física realista**: Las recompensas rebotan dentro del hexágono con gravedad y rebote
- **Efectos visuales**: Partículas, glow, sombras y efectos de luz dinámicos
- **Sistema de puntuación**: Rastrea tu score y mejor puntuación personal
- **Diseño móvil**: Optimizado para dispositivos móviles en orientación vertical
- **Arte pixel**: Interfaz con estilo pixel art retro

## 🎮 Cómo Jugar

### Objetivo
Controla la serpiente para recoger las recompensas que aparecen dentro del hexágono. Cada recompensa que recojas aumenta tu puntuación y hace que la serpiente crezca.

### Controles

**Teclado:**
- `W` / `↑` - Mover hacia arriba
- `S` / `↓` - Mover hacia abajo
- `A` / `←` - Mover hacia la izquierda
- `D` / `→` - Mover hacia la derecha
- `Enter` / `Espacio` - Iniciar juego / Reiniciar
- `R` - Reiniciar (en pantalla de Game Over)

**Mouse/Touch:**
- Clic en el botón **PLAY** para iniciar
- Clic en el botón **REINICIAR** después de Game Over

### Mecánicas del Juego

- **Serpiente**: Comienza con 3 segmentos y crece cada vez que comes una recompensa
- **Recompensas**: Aparecen dentro del hexágono y rebotan con física realista
- **Hexágono**: Rota continuamente a velocidades variables
- **Colisiones**: Si la serpiente toca los bordes del hexágono, el juego termina
- **Puntuación**: Cada recompensa recogida suma 1 punto

## 🚀 Instalación

### Requisitos

- Python 3.8 o superior
- Pygame 2.0 o superior

### Instalación de Dependencias

```bash
# Instalar Pygame
pip install pygame

# O usando requirements.txt (si está disponible)
pip install -r requirements.txt
```

### Ejecutar el Juego

```bash
python snake_pygame.py
```

## 📁 Estructura del Proyecto

```
snake_game/
├── snake_pygame.py      # Código principal del juego
├── main.py              # Punto de entrada para Android
├── assets/              # Recursos gráficos
│   ├── bonificacion.png # Imagen para recompensas y cuerpo de la serpiente
│   ├── presentacion.png # Imagen de pantalla de presentación
│   ├── reward.png       # Imagen alternativa para recompensas
│   └── snake_head.png   # Imagen de cabeza de serpiente
├── best_score.json      # Archivo que guarda el mejor score
└── README.md           # Este archivo
```

## 🎨 Características Técnicas

### Efectos Visuales

- **Partículas**: Chispas que aparecen al recoger recompensas
- **Glow**: Efectos de resplandor alrededor de recompensas y hexágono
- **Sombras**: Sombras dinámicas para profundidad visual
- **Parallax**: Fondo con efecto parallax para inmersión
- **Estrellas**: Estrellas animadas en el fondo

### Física

- **Gravedad**: Las recompensas caen dentro del hexágono
- **Rebote**: Las recompensas rebotan en los bordes con pérdida de energía
- **Rotación**: El hexágono rota a velocidades variables
- **Colisiones**: Detección precisa de colisiones circulares

### Sistema de Guardado

El juego guarda automáticamente tu mejor puntuación en `best_score.json`. El archivo se crea automáticamente la primera vez que juegas.

## 📱 Compilación para Android

El juego está diseñado para ser compilado como APK para Android usando Buildozer. Consulta la documentación de Buildozer para más detalles sobre cómo compilar para Android.

### Requisitos para Android

- Buildozer instalado
- Android SDK y NDK
- WSL (si estás en Windows)

## 🎯 Estados del Juego

1. **Presentación**: Pantalla inicial con imagen de fondo y botón PLAY
2. **Menú**: Pantalla de menú con título y instrucciones
3. **Jugando**: Estado activo del juego
4. **Game Over**: Pantalla de fin de juego con opción de reiniciar

## ⚙️ Configuración

Puedes ajustar las siguientes constantes en `snake_pygame.py`:

- `SCREEN_WIDTH` / `SCREEN_HEIGHT`: Tamaño de la pantalla
- `SNAKE_SPEED`: Velocidad de la serpiente
- `NUM_REWARDS`: Número de recompensas simultáneas
- `HEX_ROTATION_SPEED`: Velocidad de rotación del hexágono
- `GRAVITY`: Fuerza de gravedad para las recompensas
- `REWARD_BOUNCE`: Factor de rebote de las recompensas

## 🐛 Solución de Problemas

### El juego no inicia
- Verifica que Pygame esté instalado correctamente: `pip install pygame`
- Asegúrate de tener Python 3.8 o superior

### Las imágenes no se cargan
- Verifica que la carpeta `assets/` exista y contenga las imágenes necesarias
- Asegúrate de ejecutar el juego desde el directorio raíz del proyecto

### El mejor score no se guarda
- Verifica los permisos de escritura en el directorio del juego
- El archivo `best_score.json` se crea automáticamente

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Siéntete libre de usarlo, modificarlo y distribuirlo.

## 🙏 Créditos

- Desarrollado con **Pygame**
- Arte pixel art personalizado
- Efectos visuales y física implementados desde cero

## 📧 Contacto

Si tienes preguntas, sugerencias o encuentras algún bug, no dudes en abrir un issue o contribuir al proyecto.

---

¡Disfruta jugando Hex Snake Mobile! 🎮🐍

