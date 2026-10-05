"""Constantes de pantalla, estilo y dificultad de ORT Recicla."""

ANCHO = 1100
ALTO = 760
FPS = 60
DURACION_NIVEL = 45

FONDO = (224, 228, 226)
PANEL = (248, 249, 246)
TINTA = (30, 37, 39)
TINTA_SUAVE = (100, 110, 109)
BLANCO = (255, 255, 255)
NEGRO = (35, 39, 41)
AMARILLO = (242, 190, 34)
VIOLETA = (137, 85, 176)
AZUL = (54, 132, 204)
VERDE = (49, 132, 96)
ROJO = (194, 62, 58)
METAL = (64, 72, 73)
CLARO_METAL = (111, 121, 121)

TAM_TITULO = 38
TAM_GRANDE = 28
TAM_NORMAL = 20
TAM_MEDIA = 16
TAM_CHICA = 13

ANCHO_RESIDUO = 56
ALTO_RESIDUO = 64
AREA_CINTA = (42, 270, 1016, 218)
AREA_PISTA = (54, 284, 992, 190)
RECT_SILENCIO = (1010, 18, 54, 46)
RECT_PAUSA = (940, 18, 54, 46)
RECT_ACCION = (380, 624, 340, 58)

NIVELES = {
    1: {"cantidad": 20, "intervalo": 1450, "velocidad": 58},
    2: {"cantidad": 20, "intervalo": 1450, "velocidad": 88},
    3: {"cantidad": 25, "intervalo": 1120, "velocidad": 88},
    4: {"cantidad": 25, "intervalo": 1120, "velocidad": 118},
    5: {"cantidad": 30, "intervalo": 850, "velocidad": 118},
    6: {"cantidad": 30, "intervalo": 850, "velocidad": 148},
    7: {"cantidad": 35, "intervalo": 720, "velocidad": 148},
    8: {"cantidad": 40, "intervalo": 640, "velocidad": 148},
    9: {"cantidad": 40, "intervalo": 640, "velocidad": 168},
}

CONTENEDORES_CONFIG = (
    {"tipo": "plastico", "lineas": ("PLÁSTICO",),
     "color": AMARILLO, "rect": (40, 552, 245, 145)},
    {"tipo": "electronico", "lineas": ("ELECTRÓNICOS", "(RAEE)"),
     "color": VIOLETA, "rect": (305, 552, 245, 145)},
    {"tipo": "papel", "lineas": ("PAPEL Y CARTÓN",),
     "color": AZUL, "rect": (570, 552, 245, 145)},
    {"tipo": "mezclado", "lineas": ("RESIDUOS", "MEZCLADOS"),
     "color": NEGRO, "rect": (835, 552, 245, 145)},
)