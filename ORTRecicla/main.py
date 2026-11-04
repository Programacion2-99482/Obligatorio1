# Asistencia de IAG: GitHub Copilot, para implementacion y pruebas iniciales.
import array
import json
import math
import random
from pathlib import Path
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
    RECT_PAUSA as RECT_PAUSA_CONFIG,
    RECT_RANKING as RECT_RANKING_CONFIG,
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

pantalla = pygame.display.set_mode(
    (ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED
)
pygame.display.set_caption("MISIÓN Reciclaje")
reloj = pygame.time.Clock()

FUENTE_TITULO = pygame.font.SysFont("arial", TAM_TITULO, bold=True)
FUENTE_GRANDE = pygame.font.SysFont("arial", TAM_GRANDE, bold=True)
FUENTE = pygame.font.SysFont("arial", TAM_NORMAL)
FUENTE_MEDIA = pygame.font.SysFont("arial", TAM_MEDIA, bold=True)
FUENTE_CHICA = pygame.font.SysFont("arial", TAM_CHICA, bold=True)

ARCHIVO_IMAGEN_FONDO_INICIO = Path(__file__).with_name("imagenes") / "FondoR.jpg"
IMAGEN_FONDO_INICIO = pygame.transform.smoothscale(
    pygame.image.load(str(ARCHIVO_IMAGEN_FONDO_INICIO)).convert(),
    (ANCHO, ALTO),
)
ARCHIVO_IMAGEN_MANO = Path(__file__).with_name("imagenes") / "Mano.png"
IMAGEN_MANO = pygame.transform.smoothscale(
    pygame.image.load(str(ARCHIVO_IMAGEN_MANO)).convert_alpha(), (40, 40)
)
ARCHIVO_IMAGEN_PAPELERAS = Path(__file__).with_name("imagenes") / "Papeleras.jpeg"
IMAGEN_PAPELERAS_ORIGINAL = pygame.image.load(
    str(ARCHIVO_IMAGEN_PAPELERAS)
).convert()
RECORTES_PAPELERAS = {
    "plastico": pygame.Rect(28, 156, 382, 661),
    "electronico": pygame.Rect(443, 156, 374, 661),
    "papel": pygame.Rect(847, 156, 374, 661),
    "mezclado": pygame.Rect(1245, 156, 397, 661),
}
ALTO_IMAGEN_PAPELERA = CONTENEDORES_CONFIG[0]["rect"][3] + 32
DURACION_BRILLO_PAPELERA = 420
RADIO_BRILLO_PAPELERA = 48
IMAGEN_BRILLO_PAPELERA = pygame.Surface(
    (RADIO_BRILLO_PAPELERA * 2, RADIO_BRILLO_PAPELERA * 2),
    pygame.SRCALPHA,
)
for radio in range(RADIO_BRILLO_PAPELERA, 0, -1):
    opacidad = round(210 * (1 - radio / RADIO_BRILLO_PAPELERA) ** 0.8)
    pygame.draw.circle(
        IMAGEN_BRILLO_PAPELERA,
        (255, 255, 255, opacidad),
        (RADIO_BRILLO_PAPELERA, RADIO_BRILLO_PAPELERA),
        radio,
    )

def quitar_fondo_blanco(imagen):
    """Quita el fondo claro y sus sombras si están conectados al borde."""
    mascara_blancos = pygame.mask.from_threshold(
        imagen, (255, 255, 255), (85, 85, 85, 0)
    )
    fondo = pygame.mask.Mask(imagen.get_size())
    ancho, alto = imagen.get_size()
    bordes = (
        [(x, 0) for x in range(ancho)]
        + [(x, alto - 1) for x in range(ancho)]
        + [(0, y) for y in range(1, alto - 1)]
        + [(ancho - 1, y) for y in range(1, alto - 1)]
    )

    for punto in bordes:
        # Solo se quita el blanco conectado al borde para conservar detalles claros internos.
        if mascara_blancos.get_at(punto) and not fondo.get_at(punto):
            fondo.draw(mascara_blancos.connected_component(punto), (0, 0))

    imagen_con_alfa = imagen.convert_alpha()
    for y in range(alto):
        for x in range(ancho):
            if fondo.get_at((x, y)):
                imagen_con_alfa.set_at((x, y), (0, 0, 0, 0))
    return imagen_con_alfa


IMAGENES_CONTENEDORES = {
    tipo: pygame.transform.smoothscale(
        quitar_fondo_blanco(
            IMAGEN_PAPELERAS_ORIGINAL.subsurface(recorte).copy()
        ),
        (
            round(recorte.width * ALTO_IMAGEN_PAPELERA / recorte.height),
            ALTO_IMAGEN_PAPELERA,
        ),
    )
    for tipo, recorte in RECORTES_PAPELERAS.items()
}

RESIDUOS = [
    {"tipo": "mezclado", "nombre": "Cáscara de banana", "imagen": "CáscaraDeBanana.png"},
    {"tipo": "mezclado", "nombre": "Pincel", "imagen": "Pincel.png"},
    {"tipo": "mezclado", "nombre": "Caja de jugo", "imagen": "CajaJugo.png"},
    {"tipo": "mezclado", "nombre": "Medias", "imagen": "Medias.png"},
    {"tipo": "electronico", "nombre": "Teclado", "imagen": "Teclado.png"},
    {"tipo": "electronico", "nombre": "Mouse", "imagen": "Mouse.png"},
    {"tipo": "electronico", "nombre": "Placa PC", "imagen": "PlacaPC.png"},
    {"tipo": "electronico", "nombre": "Enchufe", "imagen": "Enchufe.png"},
    {"tipo": "plastico", "nombre": "Botella plástica", "imagen": "BotellaPlástica.png"},
    {"tipo": "plastico", "nombre": "Envase plástico", "imagen": "EnvasePlástico.png"},
    {"tipo": "plastico", "nombre": "Cubiertos plásticos", "imagen": "CubiertosPlásticos.png"},
    {"tipo": "plastico", "nombre": "Vaso plástico", "imagen": "VasoPlástico.png"},
    {"tipo": "papel", "nombre": "Caja de cartón", "imagen": "CajaDeCartón.png"},
    {"tipo": "papel", "nombre": "Cuaderno", "imagen": "Cuaderno.png"},
    {"tipo": "papel", "nombre": "Hoja", "imagen": "Hoja.png"},
    {"tipo": "papel", "nombre": "Post-it", "imagen": "Post-it.png"},
]

def cargar_imagen_residuo(nombre_archivo):
    """Carga cada residuo manteniendo su proporción dentro del área de juego."""
    ruta = Path(__file__).with_name("imagenes") / nombre_archivo
    imagen = pygame.image.load(str(ruta)).convert_alpha()
    escala = min(
        ANCHO_RESIDUO / imagen.get_width(),
        ALTO_RESIDUO / imagen.get_height(),
    )
    tamano = (
        round(imagen.get_width() * escala),
        round(imagen.get_height() * escala),
    )
    return pygame.transform.smoothscale(imagen, tamano)

IMAGENES_RESIDUOS = {
    nombre_archivo: cargar_imagen_residuo(nombre_archivo)
    for nombre_archivo in dict.fromkeys(residuo["imagen"] for residuo in RESIDUOS)
}

def crear_icono_portada(imagen):
    """Centra cada residuo en un recuadro uniforme sin deformar su imagen."""
    tamano = 42
    escala = min(tamano / imagen.get_width(), tamano / imagen.get_height())
    imagen_ajustada = pygame.transform.smoothscale(
        imagen,
        (
            round(imagen.get_width() * escala),
            round(imagen.get_height() * escala),
        ),
    )
    icono = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
    icono.blit(imagen_ajustada, imagen_ajustada.get_rect(center=(tamano // 2, tamano // 2)))
    return icono

IMAGENES_RESIDUOS_PORTADA = {
    nombre: crear_icono_portada(imagen)
    for nombre, imagen in IMAGENES_RESIDUOS.items()
}

CONTENEDORES = [
    {**contenedor, "rect": pygame.Rect(*contenedor["rect"])}
    for contenedor in CONTENEDORES_CONFIG
]

AREA_CINTA = pygame.Rect(*AREA_CINTA_CONFIG)
AREA_PISTA = pygame.Rect(*AREA_PISTA_CONFIG)
RECT_SILENCIO = pygame.Rect(*RECT_SILENCIO_CONFIG)
RECT_PAUSA = pygame.Rect(*RECT_PAUSA_CONFIG)
RECT_RANKING = pygame.Rect(*RECT_RANKING_CONFIG)
RECT_ACCION = pygame.Rect(*RECT_ACCION_CONFIG)
ARCHIVO_RANKING = Path(__file__).with_name("ranking.json")
LIMITE_RANKING = 5
LIMITE_NOMBRE = 10
VIDAS_INICIALES = 3

class Residuo(dict):
    """Residuo seleccionable que avanza con la banda de la cinta."""

    def __init__(self, datos, x, y):
        """Construye el residuo a partir de sus datos y su posición inicial."""
        super().__init__(datos)
        # La posición fraccionaria evita que el redondeo por fotograma altere la velocidad.
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
    # Garantiza que cada nivel incluya al menos un residuo de cada categoría.
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

def dibujar_icono_mano(superficie, x, y):
    """Dibuja la imagen de mano junto a la instrucción de control."""
    superficie.blit(IMAGEN_MANO, (x, y))

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

def dibujar_icono_pausa(superficie, rect, pausado=False):
    """Dibuja pausa o continuar dentro del botón de la cabecera."""
    centro_x, centro_y = rect.center
    if pausado:
        pygame.draw.polygon(superficie, BLANCO, [
            (centro_x - 7, centro_y - 12),
            (centro_x + 12, centro_y),
            (centro_x - 7, centro_y + 12),
        ])
    else:
        pygame.draw.rect(superficie, BLANCO, (centro_x - 10, centro_y - 12, 6, 24), border_radius=2)
        pygame.draw.rect(superficie, BLANCO, (centro_x + 4, centro_y - 12, 6, 24), border_radius=2)

def dibujar_icono_copa(superficie, rect):
    """Dibuja una copa sencilla dentro del botón de la cabecera."""
    centro_x, centro_y = rect.center
    pygame.draw.polygon(superficie, BLANCO, [
        (centro_x - 10, centro_y - 12),
        (centro_x + 10, centro_y - 12),
        (centro_x + 8, centro_y - 1),
        (centro_x + 4, centro_y + 5),
        (centro_x - 4, centro_y + 5),
        (centro_x - 8, centro_y - 1),
    ])
    pygame.draw.lines(superficie, BLANCO, False, [
        (centro_x - 10, centro_y - 8),
        (centro_x - 16, centro_y - 8),
        (centro_x - 15, centro_y),
        (centro_x - 8, centro_y + 2),
    ], 3)
    pygame.draw.lines(superficie, BLANCO, False, [
        (centro_x + 10, centro_y - 8),
        (centro_x + 16, centro_y - 8),
        (centro_x + 15, centro_y),
        (centro_x + 8, centro_y + 2),
    ], 3)
    pygame.draw.rect(superficie, BLANCO, (centro_x - 2, centro_y + 5, 4, 7))
    pygame.draw.rect(superficie, BLANCO, (centro_x - 8, centro_y + 11, 16, 3),
                     border_radius=2)

def dibujar_encabezado(silenciado):
    """Dibuja la cabecera del juego y el botón de sonido."""
    pygame.draw.rect(pantalla, TINTA, (0, 0, ANCHO, 78))
    pygame.draw.rect(pantalla, VERDE, (0, 74, ANCHO, 4))
    titulo_mision = texto(pantalla, "MISIÓN", FUENTE_TITULO, BLANCO, (38, 17))
    texto(pantalla, "Reciclaje", FUENTE_TITULO, (132, 205, 174),
          (titulo_mision.right + 9, 17))
    if estado in ("jugando", "pausa"):
        pygame.draw.rect(pantalla, (54, 63, 65), RECT_PAUSA, border_radius=12)
        dibujar_icono_pausa(pantalla, RECT_PAUSA, estado == "pausa")
    if estado in ("jugando", "pausa", "ranking"):
        pygame.draw.rect(pantalla, (54, 63, 65), RECT_RANKING, border_radius=12)
        dibujar_icono_copa(pantalla, RECT_RANKING)
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

    dibujar_icono_mano(pantalla, 53, 113)
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

    texto(pantalla, f"NIVEL {nivel} DE {len(NIVELES)}", FUENTE_CHICA, TINTA_SUAVE, (842, 109))
    texto(pantalla, f"PUNTOS  {puntaje:04d}", FUENTE_GRANDE, TINTA, (842, 126))

    texto(pantalla, f"NIVEL {nivel}", FUENTE_MEDIA, TINTA, (46, 199))
    texto(pantalla, "Clasifica cada residuo antes de que salga de la cinta",
          FUENTE_MEDIA, TINTA_SUAVE, (157, 201))
    texto(pantalla, f"VIDAS {vidas_restantes}", FUENTE_CHICA, ROJO, (696, 199))

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

def dibujar_contenedor(contenedor, rect=None, intensidad_brillo=0):
    """Dibuja una papelera con el color y rótulo de su categoría."""
    rect = contenedor["rect"] if rect is None else rect
    color = contenedor["color"]
    pygame.draw.rect(pantalla, (190, 196, 192), rect.move(0, 5), border_radius=12)
    pygame.draw.rect(pantalla, color, rect, border_radius=12)
    imagen = IMAGENES_CONTENEDORES[contenedor["tipo"]]
    destino_imagen = imagen.get_rect(midright=(rect.right - 6, rect.centery))
    ancho_texto = rect.w - imagen.get_width() - 24
    centro_texto_x = rect.x + 9 + ancho_texto // 2
    if intensidad_brillo > 0:
        IMAGEN_BRILLO_PAPELERA.set_alpha(round(255 * intensidad_brillo))
        clip_anterior = pantalla.get_clip()
        pantalla.set_clip(rect)
        pantalla.blit(
            IMAGEN_BRILLO_PAPELERA,
            IMAGEN_BRILLO_PAPELERA.get_rect(center=(centro_texto_x, rect.centery)),
        )
        pantalla.set_clip(clip_anterior)
    pantalla.blit(imagen, destino_imagen)

    inicio_texto_y = rect.centery - (len(contenedor["lineas"]) - 1) * 9
    color_texto = TINTA if contenedor["tipo"] == "plastico" else BLANCO
    for indice, linea in enumerate(contenedor["lineas"]):
        texto(pantalla, linea, FUENTE_CHICA, color_texto,
              (centro_texto_x, inicio_texto_y + indice * 19), centro=True)

def dibujar_icono_residuo(superficie, residuo, caja):
    """Dibuja el residuo usando su imagen con fondo transparente."""
    imagen = IMAGENES_RESIDUOS[residuo["imagen"]]
    superficie.blit(imagen, imagen.get_rect(center=caja.center))

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

    for contenedor in CONTENEDORES:
        intensidad_brillo = 0
        if papelera_brillo_tipo == contenedor["tipo"]:
            progreso = (
                pygame.time.get_ticks() - inicio_brillo_papelera
            ) / DURACION_BRILLO_PAPELERA
            if 0 <= progreso < 1:
                intensidad_brillo = (1 - progreso) ** 2
        dibujar_contenedor(contenedor, intensidad_brillo=intensidad_brillo)

    for residuo in residuos_activos:
        dibujar_residuo(residuo, residuo.get("seleccionado", False))

    if residuo_arrastrado is not None:
        texto(pantalla, residuo_arrastrado["nombre"], FUENTE_MEDIA, TINTA,
              (ANCHO // 2, 489), centro=True)

def dibujar_boton(rect, etiqueta):
    """Dibuja un botón de acción con su rótulo."""
    pygame.draw.rect(pantalla, VERDE, rect, border_radius=12)
    texto(pantalla, etiqueta, FUENTE_MEDIA, BLANCO, rect.center, centro=True)

def dibujar_inicio():
    """Dibuja la portada con las reglas y las categorías de reciclaje."""
    pantalla.fill(FONDO)
    pantalla.blit(IMAGEN_FONDO_INICIO, (0, 0))
    dibujar_encabezado(silenciado)
    pygame.draw.rect(pantalla, (205, 211, 208), (40, 94, 1020, 606), border_radius=20)
    pygame.draw.rect(pantalla, PANEL, (46, 100, 1008, 594), border_radius=16)
    texto(pantalla, "Arrastra cada residuo a la papelera correspondiente.",
          FUENTE_GRANDE, TINTA, (ANCHO // 2, 142), centro=True)
    texto(pantalla, f"Completa los {len(NIVELES)} niveles de {DURACION_NIVEL} segundos cada uno.",
          FUENTE_MEDIA, TINTA_SUAVE, (ANCHO // 2, 181), centro=True)
    texto(pantalla, "Un error o un residuo caído termina la partida.",
          FUENTE_CHICA, TINTA_SUAVE, (ANCHO // 2, 210), centro=True)

    for indice, contenedor in enumerate(CONTENEDORES):
        rect = pygame.Rect(52 + indice * 250, 246, 245, 145)
        dibujar_contenedor(contenedor, rect)

        residuos_categoria = [
            residuo for residuo in RESIDUOS
            if residuo["tipo"] == contenedor["tipo"]
        ]
        for indice_residuo, residuo in enumerate(residuos_categoria):
            centro_x = rect.x + round((indice_residuo + 0.5) * rect.w / 4)
            icono = IMAGENES_RESIDUOS_PORTADA[residuo["imagen"]]
            pantalla.blit(icono, icono.get_rect(center=(centro_x, 452)))

    texto(pantalla, "Sumá puntos y conseguí tu lugar en el TOP 5.",
          FUENTE_GRANDE, VERDE, (ANCHO // 2, 533), centro=True)
    dibujar_boton(RECT_ACCION, "COMENZAR (espacio)")

def dibujar_popup(titulo, detalle, indicacion, color=VERDE):
    """Dibuja el popup sobre la escena que ya está en pantalla."""
    velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    velo.fill((20, 28, 29, 175))
    pantalla.blit(velo, (0, 0))
    panel = pygame.Rect(225, 224, 650, 310)
    pygame.draw.rect(pantalla, PANEL, panel, border_radius=20)
    pygame.draw.rect(pantalla, color, (panel.x, panel.y, panel.w, 10), border_radius=6)
    texto(pantalla, titulo, FUENTE_TITULO, TINTA, (ANCHO // 2, 291), centro=True)
    texto(pantalla, detalle, FUENTE, TINTA_SUAVE, (ANCHO // 2, 356), centro=True)
    dibujar_boton(RECT_ACCION, indicacion)

def dibujar_mensaje(titulo, detalle, indicacion, color=VERDE):
    """Dibuja un panel de transición, derrota o victoria sobre la partida."""
    configuracion = NIVELES[nivel]
    transcurrido = max(0, (inicio_mensaje - inicio_nivel) / 1000)
    restante = max(0, DURACION_NIVEL - transcurrido)
    dibujar_escena(
        nivel, restante, reciclados, configuracion["cantidad"], puntaje,
        residuos_activos, transcurrido, configuracion["velocidad"],
    )
    dibujar_popup(titulo, detalle, indicacion, color)

def cargar_ranking():
    """Carga los cinco mejores puntajes guardados en el directorio del juego."""
    try:
        with ARCHIVO_RANKING.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(datos, list):
        return []
    entradas = [
        entrada for entrada in datos
        if isinstance(entrada, dict)
        and isinstance(entrada.get("nombre"), str)
        and isinstance(entrada.get("puntaje"), int)
        and isinstance(entrada.get("nivel"), int)
    ]
    return sorted(entradas, key=lambda entrada: entrada["puntaje"], reverse=True)[:LIMITE_RANKING]

def guardar_ranking():
    """Persiste el ranking actual sin interrumpir el juego si el archivo no puede escribirse."""
    try:
        with ARCHIVO_RANKING.open("w", encoding="utf-8") as archivo:
            json.dump(ranking, archivo, ensure_ascii=False, indent=2)
    except OSError:
        pass

def clasifica_para_ranking():
    """Indica si el puntaje actual entra entre los cinco primeros."""
    return len(ranking) < LIMITE_RANKING or puntaje > ranking[-1]["puntaje"]

def comenzar_fin_partida():
    """Solicita nombre solo si el puntaje entra al ranking; luego muestra resultados."""
    global estado, nombre_ingresado, inicio_mensaje
    inicio_mensaje = pygame.time.get_ticks()
    if clasifica_para_ranking():
        nombre_ingresado = ""
        estado = "ingresar_nombre"
        pygame.key.start_text_input()
    else:
        estado = "resultado"

def confirmar_nombre():
    """Agrega al ranking el nombre y los datos de la partida terminada."""
    global estado, ranking
    nombre = nombre_ingresado.strip()[:LIMITE_NOMBRE]
    if not nombre:
        return
    ranking.append({"nombre": nombre, "puntaje": puntaje, "nivel": nivel})
    ranking = sorted(ranking, key=lambda entrada: entrada["puntaje"], reverse=True)[:LIMITE_RANKING]
    guardar_ranking()
    pygame.key.stop_text_input()
    estado = "resultado"

def alternar_pausa(ahora=None):
    """Pausa o reanuda y desplaza los relojes para congelar el nivel."""
    global estado, pausa_inicio, inicio_nivel, ultimo_aparicion
    global residuo_arrastrado
    if ahora is None:
        ahora = pygame.time.get_ticks()
    if estado == "jugando":
        if residuo_arrastrado is not None:
            residuo_arrastrado["seleccionado"] = False
            residuo_arrastrado = None
        pausa_inicio = ahora
        estado = "pausa"
    elif estado == "pausa":
        duracion_pausa = ahora - pausa_inicio
        # Desplaza los relojes para que el tiempo y la aparición de residuos queden congelados.
        inicio_nivel += duracion_pausa
        ultimo_aparicion += duracion_pausa
        estado = "jugando"

def preparar_nivel(nivel_actual):
    """Crea el conjunto de residuos y reinicia los contadores del nivel."""
    cantidad = NIVELES[nivel_actual]["cantidad"]
    return preparar_residuos(cantidad), 0, pygame.time.get_ticks(), 0

def iniciar_juego():
    """Inicializa el nivel uno y el puntaje de una partida nueva."""
    global estado, nivel, puntaje, puntaje_base_nivel, vidas_restantes
    global residuos_pendientes, reciclados, inicio_nivel, ultimo_aparicion
    global indice_residuo, residuo_arrastrado, motivo_fallo
    global papelera_brillo_tipo
    global inicio_mensaje

    estado = "jugando"
    nivel = 1
    puntaje = 0
    puntaje_base_nivel = 0
    vidas_restantes = VIDAS_INICIALES
    residuos_pendientes, indice_residuo, inicio_nivel, reciclados = preparar_nivel(nivel)
    ultimo_aparicion = inicio_nivel
    residuo_arrastrado = None
    motivo_fallo = ""
    papelera_brillo_tipo = None
    inicio_mensaje = inicio_nivel

def siguiente_nivel():
    """Avanza un nivel o termina la partida al completar el último."""
    global estado, nivel, puntaje_base_nivel
    global residuos_pendientes, indice_residuo, inicio_nivel, reciclados, ultimo_aparicion
    global residuo_arrastrado

    if nivel == max(NIVELES):
        comenzar_fin_partida()
        return

    nivel += 1
    puntaje_base_nivel = puntaje
    residuos_pendientes, indice_residuo, inicio_nivel, reciclados = preparar_nivel(nivel)
    ultimo_aparicion = inicio_nivel
    residuo_arrastrado = None
    estado = "jugando"

def reintentar_nivel():
    """Reinicia el nivel actual si quedan vidas disponibles."""
    global estado, puntaje, residuos_pendientes, indice_residuo, inicio_nivel, reciclados
    global ultimo_aparicion, residuo_arrastrado, motivo_fallo

    if vidas_restantes > 0:
        # El puntaje de niveles ya superados se conserva al reintentar el nivel actual.
        puntaje = puntaje_base_nivel
        residuos_pendientes, indice_residuo, inicio_nivel, reciclados = preparar_nivel(nivel)
        ultimo_aparicion = inicio_nivel
        residuo_arrastrado = None
        motivo_fallo = ""
        estado = "jugando"

def terminar_intento(motivo):
    """Pasa a derrota y conserva el motivo que causó el fallo."""
    global estado, motivo_fallo, residuo_arrastrado, inicio_mensaje, vidas_restantes
    if estado == "jugando":
        vidas_restantes -= 1
    estado = "fallo"
    motivo_fallo = motivo
    residuo_arrastrado = None
    inicio_mensaje = pygame.time.get_ticks()

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
    global estado

    if RECT_SILENCIO.collidepoint(posicion):
        alternar_silencio()
        return
    if RECT_PAUSA.collidepoint(posicion) and estado in ("jugando", "pausa"):
        alternar_pausa()
        return
    if estado == "inicio" and RECT_ACCION.collidepoint(posicion):
        iniciar_juego()
    elif estado == "pausa" and RECT_ACCION.collidepoint(posicion):
        alternar_pausa()
    elif estado == "nivel_completado" and RECT_ACCION.collidepoint(posicion):
        siguiente_nivel()
    elif estado == "fallo" and RECT_ACCION.collidepoint(posicion):
        if vidas_restantes > 0:
            reintentar_nivel()
        else:
            comenzar_fin_partida()
    elif estado == "ingresar_nombre" and RECT_ACCION.collidepoint(posicion):
        confirmar_nombre()
    elif estado == "resultado" and RECT_ACCION.collidepoint(posicion):
        estado = "inicio"

def soltar_residuo(posicion):
    """Clasifica el objeto soltado y suma puntos o termina el intento."""
    global residuo_arrastrado, reciclados, puntaje
    global papelera_brillo_tipo, inicio_brillo_papelera

    if residuo_arrastrado is None:
        return

    residuo_arrastrado.arrastrar(posicion)
    centro_residuo = residuo_arrastrado["rect"].center
    destino = next((contenedor for contenedor in CONTENEDORES
                    if contenedor["rect"].collidepoint(centro_residuo)), None)
    if destino is None:
        residuo_arrastrado["seleccionado"] = False
        origen = residuo_arrastrado.get("posicion_origen")
        if origen is not None:
            residuo_arrastrado["rect"] = origen
            residuo_arrastrado.posicion_x = float(origen.x)
        residuo_arrastrado = None
        return

    if residuo_arrastrado["tipo"] != destino["tipo"]:
        reproducir(SONIDO_ERROR, silenciado)
        nombre_destino = " ".join(
            linea.lower() for linea in destino["lineas"]
            if not linea.startswith("(")
        )
        terminar_intento(f"{residuo_arrastrado['nombre']} no va en {nombre_destino}.")
        return

    residuos_activos.remove(residuo_arrastrado)
    residuo_arrastrado = None
    reciclados += 1
    puntaje += 100
    papelera_brillo_tipo = destino["tipo"]
    inicio_brillo_papelera = pygame.time.get_ticks()
    reproducir(SONIDO_ACIERTO, silenciado)

def dibujar_entrada_nombre():
    """Muestra el campo de nombre previo a la pantalla final."""
    dibujar_mensaje("¡Puntaje entre los 5!", "Escribe tu nombre (máximo 10 caracteres).",
                    "GUARDAR · ENTER")
    campo = pygame.Rect(330, 402, 440, 56)
    pygame.draw.rect(pantalla, BLANCO, campo, border_radius=8)
    pygame.draw.rect(pantalla, VERDE, campo, 2, border_radius=8)
    contenido = nombre_ingresado or "Tu nombre..."
    color = TINTA if nombre_ingresado else TINTA_SUAVE
    texto(pantalla, contenido, FUENTE_GRANDE, color, campo.center, centro=True)

def dibujar_resultado():
    """Dibuja el nivel y puntaje final junto al ranking persistente."""
    pantalla.fill(FONDO)
    dibujar_encabezado(silenciado)
    panel = pygame.Rect(180, 105, 740, 520)
    pygame.draw.rect(pantalla, PANEL, panel, border_radius=18)
    pygame.draw.rect(pantalla, VERDE, (panel.x, panel.y, panel.w, 9), border_radius=5)
    texto(pantalla, "JUEGO TERMINADO", FUENTE_TITULO, TINTA,
          (ANCHO // 2, 155), centro=True)
    texto(pantalla, f"Nivel alcanzado: {nivel}   ·   Puntaje final: {puntaje}",
          FUENTE_GRANDE, TINTA_SUAVE, (ANCHO // 2, 211), centro=True)
    texto(pantalla, "TOP 5", FUENTE_MEDIA, TINTA, (ANCHO // 2, 266), centro=True)

    if ranking:
        for indice, entrada in enumerate(ranking):
            y = 302 + indice * 47
            pygame.draw.line(pantalla, (220, 225, 222), (250, y + 20), (850, y + 20), 1)
            texto(pantalla, f"{indice + 1}.", FUENTE_MEDIA, TINTA_SUAVE, (270, y))
            texto(pantalla, entrada["nombre"][:LIMITE_NOMBRE], FUENTE_MEDIA,
                  TINTA, (325, y))
            texto(pantalla, f"Nivel {entrada['nivel']}", FUENTE_CHICA,
                  TINTA_SUAVE, (650, y + 2))
            texto(pantalla, f"{entrada['puntaje']} pts", FUENTE_MEDIA,
                  VERDE, (740, y))
    else:
        texto(pantalla, "Todavía no hay puntajes registrados.", FUENTE,
              TINTA_SUAVE, (ANCHO // 2, 350), centro=True)

    dibujar_boton(RECT_ACCION, "VOLVER AL INICIO (espacio)")

def dibujar_ranking():
    """Muestra el top 5 mientras conserva suspendido el estado de juego."""
    pantalla.fill(FONDO)
    dibujar_encabezado(silenciado)
    panel = pygame.Rect(180, 105, 740, 520)
    pygame.draw.rect(pantalla, PANEL, panel, border_radius=18)
    pygame.draw.rect(pantalla, VERDE, (panel.x, panel.y, panel.w, 9), border_radius=5)
    texto(pantalla, "RANKING", FUENTE_TITULO, TINTA,
          (ANCHO // 2, 155), centro=True)
    texto(pantalla, "TOP 5", FUENTE_MEDIA, TINTA, (ANCHO // 2, 222), centro=True)

    if ranking:
        for indice, entrada in enumerate(ranking):
            y = 268 + indice * 47
            pygame.draw.line(pantalla, (220, 225, 222), (250, y + 20), (850, y + 20), 1)
            texto(pantalla, f"{indice + 1}.", FUENTE_MEDIA, TINTA_SUAVE, (270, y))
            texto(pantalla, entrada["nombre"][:LIMITE_NOMBRE], FUENTE_MEDIA,
                  TINTA, (325, y))
            texto(pantalla, f"Nivel {entrada['nivel']}", FUENTE_CHICA,
                  TINTA_SUAVE, (650, y + 2))
            texto(pantalla, f"{entrada['puntaje']} pts", FUENTE_MEDIA,
                  VERDE, (740, y))
    else:
        texto(pantalla, "Todavía no hay puntajes registrados.", FUENTE,
              TINTA_SUAVE, (ANCHO // 2, 350), centro=True)

    dibujar_boton(RECT_ACCION, "VOLVER AL JUEGO (esc)")

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
        detalle = "Clasificaste todos los residuos correctamente."
        indicacion = ("SIGUIENTE NIVEL (espacio)" if nivel < max(NIVELES)
                  else "VER RESULTADO (espacio)")
        dibujar_mensaje(titulo, detalle, indicacion)
    elif estado == "pausa":
        configuracion = NIVELES[nivel]
        transcurrido = (pausa_inicio - inicio_nivel) / 1000
        restante = max(0, DURACION_NIVEL - transcurrido)
        dibujar_escena(nivel, restante, reciclados, configuracion["cantidad"], puntaje,
                       residuos_activos, transcurrido, configuracion["velocidad"])
        dibujar_popup("Reciclaje en pausa", "El tiempo y la cinta están detenidos.",
                      "CONTINUAR (espacio)")
    elif estado == "ingresar_nombre":
        dibujar_entrada_nombre()
    elif estado == "fallo":
        if vidas_restantes > 0:
            titulo = "Ups, fallaste"
            detalle = f"{motivo_fallo}  ·  Te quedan {vidas_restantes} vidas."
            indicacion = "REINTENTAR NIVEL (R)"
        else:
            titulo = "Nivel no superado"
            detalle = f"{motivo_fallo}  ·  Se agotaron las vidas."
            indicacion = "VER RESULTADO  ·  R"
        dibujar_mensaje(titulo, detalle, indicacion, ROJO)
    elif estado == "resultado":
        dibujar_resultado()
    elif estado == "ranking":
        dibujar_ranking()

estado = "inicio"
nivel = 1
puntaje = 0
puntaje_base_nivel = 0
vidas_restantes = VIDAS_INICIALES
residuos_pendientes = []
indice_residuo = 0
inicio_nivel = 0
ultimo_aparicion = 0
reciclados = 0
residuo_arrastrado = None
motivo_fallo = ""
papelera_brillo_tipo = None
inicio_brillo_papelera = 0
silenciado = False
residuos_activos = []
pausa_inicio = 0
estado_anterior_ranking = "jugando"
inicio_ranking = 0
inicio_mensaje = 0
nombre_ingresado = ""
ranking = cargar_ranking()

def alternar_ranking(ahora=None):
    """Abre el ranking durante una partida o la reanuda al volver."""
    global estado, estado_anterior_ranking, inicio_ranking
    global inicio_nivel, ultimo_aparicion, residuo_arrastrado

    if ahora is None:
        ahora = pygame.time.get_ticks()

    if estado == "ranking":
        if estado_anterior_ranking == "jugando":
            duracion_ranking = ahora - inicio_ranking
            # Consultar el ranking no consume tiempo ni cambia el ritmo de aparición.
            inicio_nivel += duracion_ranking
            ultimo_aparicion += duracion_ranking
        estado = estado_anterior_ranking
        return

    if estado not in ("jugando", "pausa"):
        return

    estado_anterior_ranking = estado
    inicio_ranking = ahora
    if estado == "jugando" and residuo_arrastrado is not None:
        residuo_arrastrado["seleccionado"] = False
        residuo_arrastrado = None
    estado = "ranking"

def ejecutar_juego():
    """Ejecuta el bucle de eventos, actualización y dibujo de Pygame."""
    global estado, indice_residuo, ultimo_aparicion, residuo_arrastrado
    global motivo_fallo, puntaje, reciclados, residuos_activos, nombre_ingresado
    global inicio_mensaje

    ejecutando = True
    while ejecutando:
        delta = reloj.tick(FPS) / 1000
        ahora = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if estado == "ranking":
                        alternar_ranking(ahora)
                    else:
                        ejecutando = False
                elif evento.key == pygame.K_p and estado in ("jugando", "pausa"):
                    alternar_pausa(ahora)
                elif estado == "pausa" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    alternar_pausa(ahora)
                elif estado == "ranking" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    alternar_ranking(ahora)
                elif estado == "ingresar_nombre":
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        confirmar_nombre()
                    elif evento.key == pygame.K_BACKSPACE:
                        nombre_ingresado = nombre_ingresado[:-1]
                elif estado == "inicio" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    iniciar_juego()
                    residuos_activos = []
                elif estado == "nivel_completado" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    siguiente_nivel()
                    residuos_activos = []
                    reproducir(SONIDO_NIVEL, silenciado)
                elif estado == "fallo" and evento.key == pygame.K_r:
                    if vidas_restantes > 0:
                        reintentar_nivel()
                        residuos_activos = []
                    else:
                        comenzar_fin_partida()
                elif estado == "resultado" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    estado = "inicio"

            elif evento.type == pygame.TEXTINPUT and estado == "ingresar_nombre":
                nombre_ingresado = (nombre_ingresado + evento.text)[:LIMITE_NOMBRE]

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if RECT_SILENCIO.collidepoint(evento.pos):
                    alternar_silencio()
                elif RECT_RANKING.collidepoint(evento.pos) and estado in (
                    "jugando", "pausa", "ranking"
                ):
                    alternar_ranking(ahora)
                elif estado in ("jugando", "pausa") and RECT_PAUSA.collidepoint(evento.pos):
                    alternar_pausa(ahora)
                elif estado == "ranking" and RECT_ACCION.collidepoint(evento.pos):
                    alternar_ranking(ahora)
                elif estado in ("inicio", "pausa", "nivel_completado", "fallo",
                                "ingresar_nombre", "resultado"):
                    anterior = estado
                    procesar_clic(evento.pos)
                    if estado == "jugando" and anterior in ("inicio", "nivel_completado", "fallo"):
                        residuos_activos = []
                        if anterior == "nivel_completado":
                            reproducir(SONIDO_NIVEL, silenciado)
                elif estado == "jugando":
                    for residuo in reversed(residuos_activos):
                        if residuo["rect"].collidepoint(evento.pos):
                            residuo_arrastrado = residuo
                            residuo["seleccionado"] = True
                            residuo["posicion_origen"] = residuo["rect"].copy()
                            break

            elif (evento.type == pygame.MOUSEMOTION and estado == "jugando"
                  and residuo_arrastrado is not None):
                residuo_arrastrado.arrastrar(evento.pos)

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if estado == "jugando" and residuo_arrastrado is not None:
                    if RECT_PAUSA.collidepoint(evento.pos):
                        alternar_pausa(ahora)
                    else:
                        soltar_residuo(evento.pos)

        if estado == "jugando":
            configuracion = NIVELES[nivel]
            tiempo_transcurrido = (ahora - inicio_nivel) / 1000
            tiempo_restante = DURACION_NIVEL - tiempo_transcurrido

            if tiempo_restante <= 0 and reciclados < configuracion["cantidad"]:
                terminar_intento("Se terminó el tiempo.")
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
                        break

                brillo_terminado = (
                    ahora - inicio_brillo_papelera >= DURACION_BRILLO_PAPELERA
                )
                # Se muestra el feedback visual completo antes de pasar a la pantalla siguiente.
                if (estado == "jugando"
                        and reciclados == configuracion["cantidad"]
                        and brillo_terminado):
                    estado = "nivel_completado"
                    inicio_mensaje = ahora
                    reproducir(SONIDO_NIVEL, silenciado)

        dibujar_estado()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    ejecutar_juego()