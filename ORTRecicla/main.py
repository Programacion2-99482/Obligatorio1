# Asistencia de IAG: GitHub Copilot, para implementacion y pruebas iniciales.
# El estudiante debe revisar el codigo y declarar este apoyo en la entrega.
import array
import math
import random
import pygame
from ajustes import (
    ALTO,
    ALTO_RESIDUO,
    AMARILLO,
    ANCHO,
    ANCHO_RESIDUO,
    AREA_CINTA as AREA_CINTA_CONFIG,
    AREA_PISTA as AREA_PISTA_CONFIG,
    AZUL,
    BLANCO,
    CLARO_METAL,
    CONTENEDORES_CONFIG,
    DURACION_NIVEL,
    FPS,
    FONDO,
    METAL,
    NIVELES,
    NEGRO,
    PANEL,
    RECT_ACCION as RECT_ACCION_CONFIG,
    RECT_SILENCIO as RECT_SILENCIO_CONFIG,
    ROJO,
    TAM_CHICA,
    TAM_GRANDE,
    TAM_MEDIA,
    TAM_NORMAL,
    TAM_TITULO,
    TINTA,
    TINTA_SUAVE,
    VERDE,
    VIOLETA,
)


pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except pygame.error:
    pass

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ORT Recicla | Misión reciclaje")
reloj = pygame.time.Clock()


FUENTE_TITULO = pygame.font.SysFont("arial", TAM_TITULO, bold=True)
FUENTE_GRANDE = pygame.font.SysFont("arial", TAM_GRANDE, bold=True)
FUENTE = pygame.font.SysFont("arial", TAM_NORMAL)
FUENTE_MEDIA = pygame.font.SysFont("arial", TAM_MEDIA, bold=True)
FUENTE_CHICA = pygame.font.SysFont("arial", TAM_CHICA, bold=True)


RESIDUOS = [
    {"tipo": "plastico", "nombre": "Botella plástica", "figura": "botella"},
    {"tipo": "plastico", "nombre": "Vaso plástico", "figura": "vaso"},
    {"tipo": "plastico", "nombre": "Envase plástico", "figura": "envase"},
    {"tipo": "papel", "nombre": "Hoja de papel", "figura": "papel"},
    {"tipo": "papel", "nombre": "Cuaderno", "figura": "cuaderno"},
    {"tipo": "papel", "nombre": "Caja de cartón", "figura": "carton"},
    {"tipo": "electronico", "nombre": "Teclado", "figura": "teclado"},
    {"tipo": "electronico", "nombre": "Mouse", "figura": "mouse"},
    {"tipo": "electronico", "nombre": "Cable", "figura": "cable"},
    {"tipo": "mezclado", "nombre": "Cáscara de banana", "figura": "banana"},
    {"tipo": "mezclado", "nombre": "Cáscara de fruta", "figura": "fruta"},
]

CONTENEDORES = [
    {**contenedor, "rect": pygame.Rect(*contenedor["rect"])}
    for contenedor in CONTENEDORES_CONFIG
]

AREA_CINTA = pygame.Rect(*AREA_CINTA_CONFIG)
AREA_PISTA = pygame.Rect(*AREA_PISTA_CONFIG)
RECT_SILENCIO = pygame.Rect(*RECT_SILENCIO_CONFIG)
RECT_ACCION = pygame.Rect(*RECT_ACCION_CONFIG)


class Residuo(dict):
    """Residuo seleccionable que avanza con la banda de la cinta."""

    def __init__(self, datos, x, y):
        """Construye el residuo a partir de sus datos y su posición inicial."""
        super().__init__(datos)
        self.posicion_x = float(x)
        self["rect"] = pygame.Rect(x, y, ANCHO_RESIDUO, ALTO_RESIDUO)
        self["seleccionado"] = False

    def avanzar(self, velocidad, delta):
        """Mueve el objeto con precisión fraccionaria según la cinta."""
        if not self["seleccionado"]:
            self.posicion_x -= velocidad * delta
            self["rect"].x = round(self.posicion_x)

    def arrastrar(self, posicion):
        """Actualiza la posición del objeto mientras se arrastra."""
        self["rect"].center = posicion
        self.posicion_x = float(self["rect"].x)


def crear_efecto(frecuencias, duracion=0.11):
    """Genera un tono corto sin necesitar archivos de sonido externos."""
    if not pygame.mixer.get_init():
        return None

    frecuencia_muestreo, _, canales = pygame.mixer.get_init()
    muestras = array.array("h")
    cantidad = int(frecuencia_muestreo * duracion)

    for frecuencia in frecuencias:
        for indice in range(cantidad):
            tiempo = indice / frecuencia_muestreo
            envolvente = 1 - indice / cantidad
            valor = int(9000 * envolvente * math.sin(2 * math.pi * frecuencia * tiempo))
            muestras.extend([valor] * canales)

    return pygame.mixer.Sound(buffer=muestras.tobytes())


SONIDO_ACIERTO = crear_efecto((660, 880))
SONIDO_ERROR = crear_efecto((210, 155), 0.16)
SONIDO_NIVEL = crear_efecto((523, 659, 784), 0.09)


def reproducir(sonido, silenciado):
    """Reproduce un efecto si existe y el audio no está silenciado."""
    if sonido is not None and not silenciado:
        sonido.play()


def preparar_residuos(cantidad):
    """Crea una lista aleatoria que siempre contiene las cuatro categorías."""
    seleccionados = [
        random.choice([residuo for residuo in RESIDUOS if residuo["tipo"] == tipo])
        for tipo in ("mezclado", "plastico", "electronico", "papel")
    ]
    seleccionados.extend(random.choices(RESIDUOS, k=cantidad - len(seleccionados)))
    random.shuffle(seleccionados)
    return [
        Residuo(
            residuo,
            ANCHO + 20,
            random.randint(AREA_PISTA.top + 12, AREA_PISTA.bottom - ALTO_RESIDUO - 12),
        )
        for residuo in seleccionados
    ]


def texto(superficie, contenido, fuente, color, posicion, centro=False):
    """Dibuja texto alineado por esquina o por centro y devuelve su rectángulo."""
    imagen = fuente.render(contenido, True, color)
    destino = imagen.get_rect()
    if centro:
        destino.center = posicion
    else:
        destino.topleft = posicion
    superficie.blit(imagen, destino)
    return destino


def dibujar_icono_mano(superficie, x, y, color):
    """Dibuja el símbolo de arrastre junto a la instrucción de control."""
    pygame.draw.circle(superficie, color, (x + 13, y + 8), 5)
    pygame.draw.line(superficie, color, (x + 13, y + 13), (x + 13, y + 29), 4)
    pygame.draw.line(superficie, color, (x + 13, y + 19), (x + 4, y + 15), 4)
    pygame.draw.line(superficie, color, (x + 13, y + 19), (x + 22, y + 15), 4)
    pygame.draw.line(superficie, color, (x + 13, y + 28), (x + 7, y + 35), 4)
    pygame.draw.line(superficie, color, (x + 13, y + 28), (x + 19, y + 35), 4)


def dibujar_icono_reloj(superficie, centro, color):
    """Dibuja el icono de cuenta regresiva."""
    pygame.draw.circle(superficie, color, centro, 17, 3)
    pygame.draw.line(superficie, color, centro, (centro[0], centro[1] - 10), 3)
    pygame.draw.line(superficie, color, centro, (centro[0] + 8, centro[1] + 5), 3)


def dibujar_estrella(superficie, centro, radio, color):
    """Dibuja una estrella rellena para el contador de objetos."""
    puntos = []
    for indice in range(10):
        angulo = -math.pi / 2 + indice * math.pi / 5
        distancia = radio if indice % 2 == 0 else radio * 0.45
        puntos.append((centro[0] + math.cos(angulo) * distancia,
                       centro[1] + math.sin(angulo) * distancia))
    pygame.draw.polygon(superficie, color, puntos)


def dibujar_icono_volumen(superficie, rect, silenciado):
    """Dibuja el altavoz y su marca de silencio cuando corresponda."""
    centro_y = rect.centery
    pygame.draw.polygon(superficie, BLANCO, [
        (rect.x + 12, centro_y - 6), (rect.x + 20, centro_y - 6),
        (rect.x + 29, centro_y - 14), (rect.x + 29, centro_y + 14),
        (rect.x + 20, centro_y + 6), (rect.x + 12, centro_y + 6),
    ])
    if silenciado:
        pygame.draw.line(superficie, (255, 119, 103), (rect.x + 34, centro_y - 9),
                         (rect.x + 45, centro_y + 9), 3)
        pygame.draw.line(superficie, (255, 119, 103), (rect.x + 45, centro_y - 9),
                         (rect.x + 34, centro_y + 9), 3)
    else:
        pygame.draw.arc(superficie, BLANCO, (rect.x + 27, centro_y - 11, 20, 22), -1.1, 1.1, 2)


def dibujar_encabezado(silenciado):
    """Dibuja la cabecera del juego y el botón de sonido."""
    pygame.draw.rect(pantalla, TINTA, (0, 0, ANCHO, 78))
    pygame.draw.rect(pantalla, VERDE, (0, 74, ANCHO, 4))
    texto(pantalla, "ORT", FUENTE_TITULO, BLANCO, (38, 17))
    texto(pantalla, "RECICLA", FUENTE_TITULO, (132, 205, 174), (122, 17))
    texto(pantalla, "MISIÓN RECICLAJE", FUENTE_MEDIA, (206, 216, 213), (322, 30))
    pygame.draw.rect(pantalla, (54, 63, 65), RECT_SILENCIO, border_radius=12)
    dibujar_icono_volumen(pantalla, RECT_SILENCIO, silenciado)


def dibujar_paneles(nivel, tiempo_restante, reciclados, cantidad, puntaje):
    """Dibuja controles, tiempo, progreso, nivel y puntaje."""
    cajas = [
        pygame.Rect(38, 96, 248, 72),
        pygame.Rect(298, 96, 210, 72),
        pygame.Rect(520, 96, 290, 72),
        pygame.Rect(822, 96, 240, 72),
    ]
    for caja in cajas:
        pygame.draw.rect(pantalla, PANEL, caja, border_radius=13)
        pygame.draw.rect(pantalla, (207, 214, 211), caja, 1, border_radius=13)

    dibujar_icono_mano(pantalla, 53, 113, VERDE)
    texto(pantalla, "SELECCIONA", FUENTE_CHICA, TINTA_SUAVE, (88, 111))
    texto(pantalla, "Y ARRASTRA", FUENTE_MEDIA, TINTA, (88, 130))

    dibujar_icono_reloj(pantalla, (330, 132), ROJO if tiempo_restante < 10 else AZUL)
    texto(pantalla, "TIEMPO", FUENTE_CHICA, TINTA_SUAVE, (356, 109))
    texto(pantalla, f"{max(0, math.ceil(tiempo_restante)):02d} s", FUENTE_GRANDE, TINTA,
          (356, 126))

    dibujar_estrella(pantalla, (550, 132), 19, AMARILLO)
    texto(pantalla, "RECICLADOS", FUENTE_CHICA, TINTA_SUAVE, (580, 108))
    texto(pantalla, f"{reciclados} / {cantidad} objetos", FUENTE_GRANDE, TINTA,
          (580, 126))

    texto(pantalla, f"NIVEL {nivel} DE 3", FUENTE_CHICA, TINTA_SUAVE, (842, 109))
    texto(pantalla, f"PUNTOS  {puntaje:04d}", FUENTE_GRANDE, TINTA, (842, 126))

    texto(pantalla, f"NIVEL {nivel}", FUENTE_MEDIA, TINTA, (46, 199))
    texto(pantalla, "Clasifica cada residuo antes de que salga de la cinta",
          FUENTE_MEDIA, TINTA_SUAVE, (157, 201))

    barra = pygame.Rect(800, 204, 250, 9)
    pygame.draw.rect(pantalla, (196, 203, 200), barra, border_radius=5)
    progreso = 1 - tiempo_restante / DURACION_NIVEL
    pygame.draw.rect(pantalla, VERDE, (barra.x, barra.y, int(barra.w * progreso), barra.h),
                     border_radius=5)


def dibujar_cinta(tiempo_transcurrido, velocidad):
    """Dibuja la cinta y mueve sus marcas a la velocidad de los residuos."""
    pygame.draw.rect(pantalla, (198, 204, 200), AREA_CINTA, border_radius=24)
    pygame.draw.rect(pantalla, METAL, AREA_PISTA, border_radius=18)
    pygame.draw.rect(pantalla, (29, 34, 36), (AREA_PISTA.x, AREA_PISTA.y + 13,
                                             AREA_PISTA.w, AREA_PISTA.h - 26),
                     border_radius=8)
    pygame.draw.line(pantalla, CLARO_METAL, (AREA_PISTA.x + 9, AREA_PISTA.y + 8),
                     (AREA_PISTA.right - 9, AREA_PISTA.y + 8), 4)
    pygame.draw.line(pantalla, CLARO_METAL, (AREA_PISTA.x + 9, AREA_PISTA.bottom - 8),
                     (AREA_PISTA.right - 9, AREA_PISTA.bottom - 8), 4)

    desplazamiento = int(tiempo_transcurrido * velocidad) % 48
    for x in range(AREA_PISTA.x + 12 - desplazamiento, AREA_PISTA.right, 48):
        pygame.draw.line(pantalla, (76, 85, 86), (x, AREA_PISTA.y + 19),
                         (x, AREA_PISTA.bottom - 19), 3)
    for x in range(AREA_PISTA.x + 24, AREA_PISTA.right - 10, 90):
        pygame.draw.circle(pantalla, (166, 173, 169), (x, AREA_PISTA.y + 8), 3)
        pygame.draw.circle(pantalla, (166, 173, 169), (x, AREA_PISTA.bottom - 8), 3)


def dibujar_contenedor(contenedor):
    """Dibuja una papelera con el color y rótulo de su categoría."""
    rect = contenedor["rect"]
    color = contenedor["color"]
    pygame.draw.rect(pantalla, (190, 196, 192), rect.move(0, 5), border_radius=12)
    pygame.draw.rect(pantalla, color, rect, border_radius=12)
    borde = tuple(max(0, canal - 28) for canal in color)
    pygame.draw.rect(pantalla, borde, (rect.x + 8, rect.y + 8, rect.w - 16, 30),
                     border_radius=8)
    pygame.draw.rect(pantalla, (26, 31, 33), (rect.x + 18, rect.y + 14,
                                             rect.w - 36, 17), border_radius=8)
    for indice, linea in enumerate(contenedor["lineas"]):
        texto(pantalla, linea, FUENTE_MEDIA, BLANCO,
              (rect.centerx, rect.y + 59 + indice * 19), centro=True)


def dibujar_icono_residuo(superficie, residuo, caja):
    """Dibuja la silueta individual del residuo sin un fondo de tarjeta."""
    x = caja.x + 4
    y = caja.y + 2
    centro_x = x + 22
    figura = residuo["figura"]

    if figura == "botella":
        pygame.draw.rect(superficie, (89, 177, 213), (x + 11, y + 13, 23, 43), border_radius=6)
        pygame.draw.rect(superficie, (89, 177, 213), (x + 16, y + 4, 13, 13))
        pygame.draw.rect(superficie, (52, 111, 143), (x + 17, y, 11, 6), border_radius=2)
        pygame.draw.rect(superficie, (201, 237, 239), (x + 13, y + 27, 19, 8), border_radius=3)
    elif figura == "vaso":
        pygame.draw.polygon(superficie, (97, 179, 210),
                            [(x + 8, y + 12), (x + 37, y + 12), (x + 32, y + 52), (x + 14, y + 52)])
        pygame.draw.line(superficie, (236, 247, 246), (x + 12, y + 17), (x + 34, y + 17), 3)
    elif figura == "envase":
        pygame.draw.rect(superficie, (82, 169, 202), (x + 7, y + 16, 33, 35), border_radius=6)
        pygame.draw.rect(superficie, (193, 230, 230), (x + 11, y + 22, 25, 10), border_radius=3)
        pygame.draw.rect(superficie, (61, 133, 164), (x + 14, y + 11, 18, 7), border_radius=3)
    elif figura == "papel":
        pygame.draw.rect(superficie, (250, 249, 240), (x + 7, y + 5, 32, 49), border_radius=3)
        for linea in range(4):
            pygame.draw.line(superficie, (115, 151, 167), (x + 12, y + 18 + linea * 8),
                             (x + 34, y + 18 + linea * 8), 2)
    elif figura == "cuaderno":
        pygame.draw.rect(superficie, (229, 241, 238), (x + 8, y + 5, 31, 49), border_radius=3)
        pygame.draw.line(superficie, (53, 132, 204), (x + 15, y + 8), (x + 15, y + 51), 3)
        for linea in range(4):
            pygame.draw.line(superficie, (145, 176, 181), (x + 19, y + 18 + linea * 8),
                             (x + 34, y + 18 + linea * 8), 2)
    elif figura == "carton":
        pygame.draw.polygon(superficie, (190, 139, 81),
                            [(x + 6, y + 19), (x + 22, y + 9), (x + 40, y + 19),
                             (x + 40, y + 45), (x + 22, y + 55), (x + 6, y + 45)])
        pygame.draw.line(superficie, (235, 200, 151), (x + 22, y + 10), (x + 22, y + 54), 2)
        pygame.draw.line(superficie, (235, 200, 151), (x + 7, y + 20), (x + 22, y + 29), 2)
    elif figura == "teclado":
        pygame.draw.rect(superficie, (76, 86, 90), (x + 3, y + 15, 41, 31), border_radius=5)
        for fila in range(3):
            for columna in range(5):
                pygame.draw.rect(superficie, (206, 211, 205),
                                 (x + 8 + columna * 7, y + 20 + fila * 7, 4, 4), border_radius=1)
    elif figura == "mouse":
        pygame.draw.ellipse(superficie, (108, 120, 122), (x + 11, y + 5, 25, 49))
        pygame.draw.line(superficie, (225, 229, 223), (x + 23, y + 9), (x + 23, y + 25), 2)
        pygame.draw.line(superficie, (225, 229, 223), (x + 23, y + 22), (x + 23, y + 33), 2)
    elif figura == "cable":
        color_cable = (216, 224, 219)
        pygame.draw.arc(superficie, color_cable, (x + 4, y + 7, 39, 43), 0.2, 5.9, 5)
        pygame.draw.line(superficie, color_cable, (x + 7, y + 26), (x + 2, y + 26), 5)
        pygame.draw.line(superficie, color_cable, (x + 40, y + 28), (x + 45, y + 28), 5)
    elif figura == "banana":
        pygame.draw.arc(superficie, (227, 186, 54), (x + 2, y + 11, 43, 37), 0.1, 2.9, 9)
        pygame.draw.line(superficie, (115, 105, 56), (x + 4, y + 28), (x + 9, y + 32), 4)
        pygame.draw.line(superficie, (115, 105, 56), (x + 39, y + 28), (x + 44, y + 24), 4)
    elif figura == "fruta":
        pygame.draw.circle(superficie, (193, 105, 74), (centro_x, y + 31), 18)
        pygame.draw.line(superficie, (94, 105, 59), (centro_x, y + 14), (centro_x + 2, y + 7), 3)
        pygame.draw.ellipse(superficie, (85, 145, 92), (centro_x + 1, y + 6, 12, 7))


def dibujar_residuo(residuo, seleccionado=False):
    """Dibuja el objeto aislado y resalta su silueta mientras se arrastra."""
    caja = residuo["rect"]
    if seleccionado:
        pygame.draw.circle(pantalla, VERDE, caja.center, 36, 2)
    dibujar_icono_residuo(pantalla, residuo, caja)


def dibujar_escena(nivel, tiempo_restante, reciclados, cantidad, puntaje,
                   residuos_activos, tiempo_transcurrido, velocidad):
    """Dibuja la cinta, sus residuos en movimiento y las cuatro papeleras."""
    pantalla.fill(FONDO)
    dibujar_encabezado(silenciado)
    dibujar_paneles(nivel, tiempo_restante, reciclados, cantidad, puntaje)
    dibujar_cinta(tiempo_transcurrido, velocidad)

    for residuo in residuos_activos:
        dibujar_residuo(residuo, residuo.get("seleccionado", False))

    if residuo_arrastrado is not None:
        texto(pantalla, residuo_arrastrado["nombre"], FUENTE_MEDIA, TINTA,
              (ANCHO // 2, 489), centro=True)
    texto(pantalla, "DESTINO DEL RESIDUO", FUENTE_MEDIA, TINTA_SUAVE, (45, 517))
    for contenedor in CONTENEDORES:
        dibujar_contenedor(contenedor)


def dibujar_boton(rect, etiqueta):
    """Dibuja un botón de acción con su rótulo."""
    pygame.draw.rect(pantalla, VERDE, rect, border_radius=12)
    texto(pantalla, etiqueta, FUENTE_MEDIA, BLANCO, rect.center, centro=True)


def dibujar_inicio():
    """Dibuja la portada con los tres niveles y las reglas básicas."""
    pantalla.fill(FONDO)
    dibujar_encabezado(silenciado)
    pygame.draw.rect(pantalla, (205, 211, 208), (40, 110, 1020, 450), border_radius=20)
    pygame.draw.rect(pantalla, PANEL, (46, 116, 1008, 438), border_radius=16)
    texto(pantalla, "Misión reciclaje", FUENTE_TITULO, TINTA, (ANCHO // 2, 177), centro=True)
    texto(pantalla, "Arrastra cada residuo al contenedor que le corresponde.",
          FUENTE, TINTA_SUAVE, (ANCHO // 2, 231), centro=True)

    resumen = [
        ("20", "objetos", "45 segundos", NEGRO),
        ("25", "objetos", "Más velocidad", AMARILLO),
        ("30", "objetos", "Ritmo máximo", VIOLETA),
    ]
    for indice, (cantidad, etiqueta, detalle, color) in enumerate(resumen):
        rect = pygame.Rect(145 + indice * 275, 288, 230, 126)
        pygame.draw.rect(pantalla, color, rect, border_radius=14)
        texto(pantalla, f"NIVEL {indice + 1}", FUENTE_CHICA, BLANCO,
              (rect.centerx, rect.y + 25), centro=True)
        texto(pantalla, cantidad, FUENTE_TITULO, BLANCO,
              (rect.centerx, rect.y + 64), centro=True)
        texto(pantalla, f"{etiqueta} · {detalle}", FUENTE_CHICA, BLANCO,
              (rect.centerx, rect.y + 103), centro=True)

    texto(pantalla, "Plástico · Papel y cartón · Electrónicos RAEE · Residuos mezclados",
          FUENTE_MEDIA, TINTA, (ANCHO // 2, 464), centro=True)
    texto(pantalla, "ORT: más de 8 t de papel/cartón recicladas en 2024; casi 3 t de RAEE al año (2022-24).",
          FUENTE_CHICA, TINTA, (ANCHO // 2, 500), centro=True)
    texto(pantalla, "Fuente: Universidad ORT Uruguay, Cómo funciona ORT Recicla y qué impacto genera.",
          FUENTE_CHICA, TINTA_SUAVE, (ANCHO // 2, 524), centro=True)
    dibujar_boton(RECT_ACCION, "COMENZAR  ·  ESPACIO")
    texto(pantalla, "Un error o un residuo perdido termina el intento.", FUENTE_CHICA,
          TINTA_SUAVE, (ANCHO // 2, 711), centro=True)


def dibujar_mensaje(titulo, detalle, indicacion, color=VERDE):
    """Dibuja un panel de transición, derrota o victoria sobre la partida."""
    dibujar_escena(1, DURACION_NIVEL, 0, 0, 0, [], 0, NIVELES[1]["velocidad"])
    velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    velo.fill((20, 28, 29, 175))
    pantalla.blit(velo, (0, 0))
    panel = pygame.Rect(225, 224, 650, 310)
    pygame.draw.rect(pantalla, PANEL, panel, border_radius=20)
    pygame.draw.rect(pantalla, color, (panel.x, panel.y, panel.w, 10), border_radius=6)
    texto(pantalla, titulo, FUENTE_TITULO, TINTA, (ANCHO // 2, 291), centro=True)
    texto(pantalla, detalle, FUENTE, TINTA_SUAVE, (ANCHO // 2, 356), centro=True)
    dibujar_boton(RECT_ACCION, indicacion)


def preparar_nivel(nivel_actual):
    """Crea el conjunto de residuos y reinicia los contadores del nivel."""
    cantidad = NIVELES[nivel_actual]["cantidad"]
    return preparar_residuos(cantidad), 0, pygame.time.get_ticks(), 0


def iniciar_juego():
    """Inicializa el nivel uno y el puntaje de una partida nueva."""
    global estado, nivel, puntaje, puntaje_base_nivel, extras_restantes
    global residuos_pendientes, reciclados, inicio_nivel, ultimo_aparicion
    global indice_residuo, residuo_arrastrado, motivo_fallo

    estado = "jugando"
    nivel = 1
    puntaje = 0
    puntaje_base_nivel = 0
    extras_restantes = 2
    residuos_pendientes, indice_residuo, inicio_nivel, reciclados = preparar_nivel(nivel)
    ultimo_aparicion = inicio_nivel
    residuo_arrastrado = None
    motivo_fallo = ""


def siguiente_nivel():
    """Avanza un nivel o declara la victoria al terminar el tercero."""
    global estado, nivel, puntaje_base_nivel, extras_restantes
    global residuos_pendientes, indice_residuo, inicio_nivel, reciclados, ultimo_aparicion
    global residuo_arrastrado

    if nivel == 3:
        estado = "victoria"
        return

    nivel += 1
    puntaje_base_nivel = puntaje
    extras_restantes = 2
    residuos_pendientes, indice_residuo, inicio_nivel, reciclados = preparar_nivel(nivel)
    ultimo_aparicion = inicio_nivel
    residuo_arrastrado = None
    estado = "jugando"


def reintentar_nivel():
    """Reinicia el nivel actual y consume una oportunidad adicional."""
    global estado, puntaje, residuos_pendientes, indice_residuo, inicio_nivel, reciclados
    global ultimo_aparicion, extras_restantes, residuo_arrastrado, motivo_fallo

    if extras_restantes > 0:
        extras_restantes -= 1
        puntaje = puntaje_base_nivel
        residuos_pendientes, indice_residuo, inicio_nivel, reciclados = preparar_nivel(nivel)
        ultimo_aparicion = inicio_nivel
        residuo_arrastrado = None
        motivo_fallo = ""
        estado = "jugando"


def terminar_intento(motivo):
    """Pasa a derrota y conserva el motivo que causó el fallo."""
    global estado, motivo_fallo, residuo_arrastrado
    estado = "fallo"
    motivo_fallo = motivo
    residuo_arrastrado = None


def alternar_silencio():
    """Alterna el audio y actualiza el volumen de cada efecto."""
    global silenciado
    silenciado = not silenciado
    volumen = 0 if silenciado else 0.45
    for sonido in (SONIDO_ACIERTO, SONIDO_ERROR, SONIDO_NIVEL):
        if sonido is not None:
            sonido.set_volume(volumen)


def procesar_clic(posicion):
    """Activa botones de portada, transición, derrota o victoria."""
    global estado, record

    if RECT_SILENCIO.collidepoint(posicion):
        alternar_silencio()
        return
    if estado == "inicio" and RECT_ACCION.collidepoint(posicion):
        iniciar_juego()
    elif estado == "nivel_completado" and RECT_ACCION.collidepoint(posicion):
        siguiente_nivel()
    elif estado == "fallo" and RECT_ACCION.collidepoint(posicion):
        if extras_restantes > 0:
            reintentar_nivel()
        else:
            estado = "inicio"
    elif estado == "victoria" and RECT_ACCION.collidepoint(posicion):
        record = max(record, puntaje)
        estado = "inicio"


def soltar_residuo(posicion):
    """Clasifica el objeto soltado y suma puntos o termina el intento."""
    global residuo_arrastrado, reciclados, puntaje, record

    if residuo_arrastrado is None:
        return

    destino = next((contenedor for contenedor in CONTENEDORES
                    if contenedor["rect"].collidepoint(posicion)), None)
    if destino is None:
        residuo_arrastrado["seleccionado"] = False
        residuo_arrastrado = None
        return

    if residuo_arrastrado["tipo"] != destino["tipo"]:
        reproducir(SONIDO_ERROR, silenciado)
        terminar_intento(f"{residuo_arrastrado['nombre']} no va en {destino['lineas'][0].lower()}.")
        record = max(record, puntaje)
        return

    residuos_activos.remove(residuo_arrastrado)
    residuo_arrastrado = None
    reciclados += 1
    puntaje += 100
    reproducir(SONIDO_ACIERTO, silenciado)


def dibujar_estado():
    """Dibuja la pantalla correspondiente al estado actual del juego."""
    if estado == "inicio":
        dibujar_inicio()
    elif estado == "jugando":
        configuracion = NIVELES[nivel]
        transcurrido = (pygame.time.get_ticks() - inicio_nivel) / 1000
        restante = max(0, DURACION_NIVEL - transcurrido)
        dibujar_escena(nivel, restante, reciclados, configuracion["cantidad"], puntaje,
                       residuos_activos, transcurrido, configuracion["velocidad"])
    elif estado == "nivel_completado":
        titulo = f"¡Nivel {nivel} superado!"
        detalle = "Separaste todos los residuos correctamente."
        indicacion = "SIGUIENTE NIVEL  ·  ESPACIO" if nivel < 3 else "VER RESULTADO  ·  ESPACIO"
        dibujar_mensaje(titulo, detalle, indicacion)
    elif estado == "fallo":
        if extras_restantes > 0:
            titulo = "Intento terminado"
            detalle = f"{motivo_fallo}  ·  Quedan {extras_restantes} intentos extra."
            indicacion = "REINTENTAR NIVEL  ·  R"
        else:
            titulo = "Nivel no superado"
            detalle = f"{motivo_fallo}  ·  Se agotaron los intentos extra."
            indicacion = "VOLVER AL INICIO  ·  R"
        dibujar_mensaje(titulo, detalle, indicacion, ROJO)
    elif estado == "victoria":
        dibujar_mensaje("¡Misión cumplida!", f"Puntaje final: {puntaje} puntos.",
                        "JUGAR DE NUEVO  ·  ESPACIO")


estado = "inicio"
nivel = 1
puntaje = 0
puntaje_base_nivel = 0
record = 0
extras_restantes = 2
residuos_pendientes = []
indice_residuo = 0
inicio_nivel = 0
ultimo_aparicion = 0
reciclados = 0
residuo_arrastrado = None
motivo_fallo = ""
silenciado = False
residuos_activos = []


def ejecutar_juego():
    """Ejecuta el bucle de eventos, actualización y dibujo de Pygame."""
    global estado, indice_residuo, ultimo_aparicion, residuo_arrastrado
    global motivo_fallo, puntaje, reciclados, record, residuos_activos

    ejecutando = True
    while ejecutando:
        delta = reloj.tick(FPS) / 1000
        ahora = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                elif estado == "inicio" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    iniciar_juego()
                    residuos_activos = []
                elif estado == "nivel_completado" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    siguiente_nivel()
                    residuos_activos = []
                    reproducir(SONIDO_NIVEL, silenciado)
                elif estado == "fallo" and evento.key == pygame.K_r:
                    if extras_restantes > 0:
                        reintentar_nivel()
                        residuos_activos = []
                    else:
                        estado = "inicio"
                elif estado == "victoria" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    record = max(record, puntaje)
                    estado = "inicio"

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if RECT_SILENCIO.collidepoint(evento.pos):
                    alternar_silencio()
                elif estado in ("inicio", "nivel_completado", "fallo", "victoria"):
                    anterior = estado
                    procesar_clic(evento.pos)
                    if estado == "jugando" and anterior != "jugando":
                        residuos_activos = []
                        if anterior == "nivel_completado":
                            reproducir(SONIDO_NIVEL, silenciado)
                elif estado == "jugando":
                    for residuo in reversed(residuos_activos):
                        if residuo["rect"].collidepoint(evento.pos):
                            residuo_arrastrado = residuo
                            residuo["seleccionado"] = True
                            break

            elif evento.type == pygame.MOUSEMOTION and residuo_arrastrado is not None:
                residuo_arrastrado.arrastrar(evento.pos)

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if estado == "jugando" and residuo_arrastrado is not None:
                    soltar_residuo(evento.pos)

        if estado == "jugando":
            configuracion = NIVELES[nivel]
            tiempo_transcurrido = (ahora - inicio_nivel) / 1000
            tiempo_restante = DURACION_NIVEL - tiempo_transcurrido

            if tiempo_restante <= 0:
                terminar_intento("Se terminó el tiempo.")
                record = max(record, puntaje)
            else:
                if (indice_residuo < configuracion["cantidad"]
                        and ahora - ultimo_aparicion >= configuracion["intervalo"]):
                    residuo = residuos_pendientes[indice_residuo]
                    residuos_activos.append(residuo)
                    indice_residuo += 1
                    ultimo_aparicion = ahora

                for residuo in list(residuos_activos):
                    if residuo is residuo_arrastrado:
                        continue
                    residuo.avanzar(configuracion["velocidad"], delta)
                    if residuo["rect"].right < AREA_PISTA.left:
                        terminar_intento(f"Se perdió {residuo['nombre']} en la cinta.")
                        record = max(record, puntaje)
                        break

                if estado == "jugando" and reciclados == configuracion["cantidad"]:
                    estado = "nivel_completado"
                    reproducir(SONIDO_NIVEL, silenciado)

        dibujar_estado()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    ejecutar_juego()