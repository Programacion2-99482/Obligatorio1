"""Genera el informe PDF de MISIÓN Reciclaje."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


SALIDA = Path(__file__).with_name("Informe_ORT_Recicla.pdf")
ANCHO, ALTO = A4
TINTA = colors.HexColor("#202729")
VERDE = colors.HexColor("#318460")
VERDE_CLARO = colors.HexColor("#DCEBE4")
GRIS = colors.HexColor("#687271")
FONDO = colors.HexColor("#F4F6F2")
AMARILLO = colors.HexColor("#F2BE22")
VIOLETA = colors.HexColor("#8955B0")
AZUL = colors.HexColor("#3684CC")
ROJO = colors.HexColor("#C23E3A")
NEGRO = colors.HexColor("#232729")

ESTILO_TEXTO = ParagraphStyle(
    "texto", fontName="Helvetica", fontSize=10, leading=15, textColor=TINTA
)
ESTILO_CENTRADO = ParagraphStyle(
    "centrado", parent=ESTILO_TEXTO, alignment=TA_CENTER
)
ESTILO_CHICO = ParagraphStyle(
    "chico", fontName="Helvetica", fontSize=8, leading=11, textColor=GRIS
)


def parrafo(pdf, contenido, x, y, ancho, estilo=ESTILO_TEXTO):
    """Dibuja un párrafo ajustado al ancho y devuelve la siguiente coordenada y."""
    bloque = Paragraph(contenido, estilo)
    _, alto = bloque.wrap(ancho, ALTO)
    bloque.drawOn(pdf, x, y - alto)
    return y - alto - 12


def titulo_pagina(pdf, numero, titulo):
    """Dibuja la banda de encabezado de las páginas del informe."""
    pdf.setFillColor(TINTA)
    pdf.rect(0, ALTO - 72, ANCHO, 72, fill=1, stroke=0)
    pdf.setFillColor(VERDE)
    pdf.rect(0, ALTO - 76, ANCHO, 4, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawString(38, ALTO - 44, titulo)
    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(ANCHO - 36, ALTO - 44, f"ORT RECICLA  ·  {numero}/4")


def caja(pdf, x, y, ancho, alto, contenido, color, texto_color=colors.white):
    """Dibuja un bloque con texto centrado para el diagrama de flujo."""
    pdf.setFillColor(color)
    pdf.roundRect(x, y, ancho, alto, 8, fill=1, stroke=0)
    estilo = ParagraphStyle(
        "nodo", fontName="Helvetica-Bold", fontSize=8, leading=10,
        textColor=texto_color, alignment=TA_CENTER,
    )
    parrafo_nodo = Paragraph(contenido, estilo)
    texto_ancho, texto_alto = parrafo_nodo.wrap(ancho - 14, alto - 8)
    parrafo_nodo.drawOn(pdf, x + (ancho - texto_ancho) / 2, y + (alto - texto_alto) / 2)


def flecha(pdf, x1, y1, x2, y2, etiqueta=""):
    """Dibuja una flecha entre dos estados del flujo."""
    pdf.setStrokeColor(GRIS)
    pdf.setFillColor(GRIS)
    pdf.setLineWidth(1.3)
    pdf.line(x1, y1, x2, y2)
    angulo = __import__("math").atan2(y2 - y1, x2 - x1)
    largo = 7
    pdf.line(x2, y2, x2 - largo * __import__("math").cos(angulo - 0.45),
             y2 - largo * __import__("math").sin(angulo - 0.45))
    pdf.line(x2, y2, x2 - largo * __import__("math").cos(angulo + 0.45),
             y2 - largo * __import__("math").sin(angulo + 0.45))
    if etiqueta:
        pdf.setFont("Helvetica-Bold", 7)
        pdf.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 4, etiqueta)


def pagina_inspiracion(pdf):
    """Escribe la inspiración y el contexto de ORT Recicla."""
    titulo_pagina(pdf, 1, "Inspiración y concepto")
    y = ALTO - 112
    y = parrafo(pdf, "<b>ORT Recicla: Misión reciclaje</b>", 42, y, ANCHO - 84,
                ParagraphStyle("bajada", parent=ESTILO_TEXTO, fontSize=14, leading=20))
    y = parrafo(pdf,
        "La idea nace de la consigna del obligatorio, de la imagen de una cinta "
        "transportadora compartida como referencia y del programa ORT Recicla. "
        "El juego convierte la separación de residuos en una tarea arcade: reconocer "
        "un objeto, decidir su categoría y depositarlo antes de que abandone la cinta.",
        42, y, ANCHO - 84)
    y = parrafo(pdf, "Referencias tomadas", 42, y, ANCHO - 84,
                ParagraphStyle("h2", parent=ESTILO_TEXTO, fontName="Helvetica-Bold", fontSize=12))
    y = parrafo(pdf,
        "<b>ORT Recicla:</b> separación por materiales, señalización de papeleras y "
        "concientización ambiental. El azul representa papel y cartón, el amarillo "
        "plásticos y el violeta RAEE, según la consigna y la referencia institucional. "
        "<b>La imagen de la cinta:</b> aporta el movimiento continuo y la presión del "
        "tiempo; se conservaron esos elementos como mecánica, no como una copia visual.",
        42, y, ANCHO - 84)

    pdf.setFillColor(VERDE_CLARO)
    pdf.roundRect(42, y - 92, ANCHO - 84, 76, 9, fill=1, stroke=0)
    parrafo(pdf,
        "<b>Impacto citado por ORT:</b> más de 8 toneladas de papel y cartón recicladas "
        "en 2024; los RAEE alcanzaron casi 3 toneladas recicladas por año entre 2022 "
        "y 2024. Estos datos aparecen también en la portada del juego.",
        56, y - 32, ANCHO - 112, ESTILO_TEXTO)
    y -= 112
    parrafo(pdf,
        "<b>Fuente:</b> Universidad ORT Uruguay, "
        "<link href='https://www.ort.edu.uy/la-universidad/sostenibilidad/como-funciona-ort-recicla-y-que-impacto-genera' "
        "color='#318460'>Cómo funciona el programa ORT Recicla y qué impacto genera</link>.",
        42, y, ANCHO - 84, ESTILO_CHICO)
    y = parrafo(pdf, "Autor/a e ID de estudiante: completar antes de entregar.",
                 42, 112, ANCHO - 84, ESTILO_CHICO)
    pdf.showPage()


def pagina_flujo(pdf):
    """Dibuja los estados y decisiones principales de la partida."""
    titulo_pagina(pdf, 2, "Diagrama de flujo del jugador")
    caja(pdf, 205, 720, 185, 38, "INICIO", VERDE)
    caja(pdf, 205, 644, 185, 48, "Preparar nivel<br/>20–40 objetos · 45 s", TINTA)
    caja(pdf, 205, 564, 185, 48, "Seleccionar y arrastrar<br/>un residuo", AZUL)
    caja(pdf, 205, 475, 185, 52, "¿Lo soltó en la categoría correcta?", AMARILLO, TINTA)
    flecha(pdf, 297, 720, 297, 692)
    flecha(pdf, 297, 644, 297, 612)
    flecha(pdf, 297, 564, 297, 527)

    caja(pdf, 412, 476, 140, 48, "Error, tiempo agotado<br/>o residuo perdido", ROJO)
    flecha(pdf, 390, 500, 412, 500, "NO")
    caja(pdf, 405, 386, 155, 48, "¿Quedan reintentos<br/>en este nivel?", TINTA)
    flecha(pdf, 482, 476, 482, 434)
    caja(pdf, 410, 300, 145, 42, "Derrota", ROJO)
    flecha(pdf, 482, 386, 482, 342, "NO")
    flecha(pdf, 405, 409, 350, 668, "SÍ: repetir nivel")

    caja(pdf, 205, 382, 185, 48, "¿Quedan objetos\npor clasificar?", TINTA)
    flecha(pdf, 297, 475, 297, 430, "SÍ")
    flecha(pdf, 297, 430, 297, 612, "SÍ: continuar")
    caja(pdf, 205, 284, 185, 48, "¿Era el nivel 9?", TINTA)
    flecha(pdf, 297, 382, 297, 332, "NO")
    caja(pdf, 70, 194, 165, 48, "Iniciar siguiente nivel", AZUL)
    caja(pdf, 260, 194, 145, 48, "VICTORIA", VERDE)
    flecha(pdf, 260, 284, 180, 242, "NO")
    flecha(pdf, 330, 284, 335, 242, "SÍ")
    flecha(pdf, 152, 242, 205, 668, "continuar")

    parrafo(pdf,
        "Un acierto suma 100 puntos. La partida solo avanza cuando se clasifican "
        "todos los objetos del nivel; se pierde al cometer un error, dejar pasar "
        "un residuo o agotar los 45 segundos.",
        42, 145, ANCHO - 84, ESTILO_CHICO)
    pdf.showPage()


def pagina_proceso(pdf):
    """Resume decisiones creativas, mecánicas y pruebas del juego."""
    titulo_pagina(pdf, 3, "Proceso creativo")
    y = ALTO - 112
    bloques = [
        ("1. De una acción a una partida", "La mecánica pasó de arrastrar una pieza "
         "a clasificar un flujo completo de residuos. La secuencia es aleatoria, "
         "pero garantiza las cuatro categorías en cada nivel. La dificultad crece "
         "en nueve niveles: 20, 20, 25, 25, 30, 30, 35, 40 y 40 objetos, a 58, "
         "88, 88, 118, 118, 148, 148, 148 y 168 px/s."),
        ("2. Forma visual", "El primer prototipo presentaba cada residuo dentro de "
         "una tarjeta. Se descartó ese marco a pedido de la persona autora y se "
         "dibujaron siluetas independientes (botella, vaso, hoja, cuaderno, teclado, "
         "mouse, cable y cáscara) directamente sobre la cinta."),
        ("3. Movimiento y respuesta", "Las marcas de la cinta y los residuos comparten "
         "la misma velocidad. Se conserva la coordenada horizontal con precisión "
         "fraccionaria para que el nivel lento también avance a 60 cuadros por segundo. "
         "Los objetos se congelan mientras se arrastran."),
        ("4. Sonido y validación", "Se eligieron tonos breves generados por código: "
         "uno ascendente para el acierto y otro grave para el error, con control de "
         "silencio. Se probaron cantidades/categorías, puntaje, derrota, reintentos, "
         "progresión y renderizado con Pygame."),
    ]
    for encabezado, cuerpo in bloques:
        y = parrafo(pdf, encabezado, 42, y, ANCHO - 84,
                    ParagraphStyle("h3", parent=ESTILO_TEXTO,
                                   fontName="Helvetica-Bold", fontSize=11))
        y = parrafo(pdf, cuerpo, 42, y, ANCHO - 84)

    pdf.setFillColor(FONDO)
    pdf.roundRect(42, 108, ANCHO - 84, 78, 8, fill=1, stroke=0)
    parrafo(pdf,
        "<b>Recursos:</b> no se incorporaron imágenes ni sonidos externos. Las formas "
        "se dibujan con Pygame y los efectos se sintetizan al iniciar. "
        "<b>IA generativa:</b> GitHub Copilot se utilizó como apoyo de ideación, "
        "implementación y pruebas iniciales; el código debe ser revisado por el estudiante.",
        55, 165, ANCHO - 110, ESTILO_CHICO)
    pdf.showPage()


def generar_pdf():
    """Genera las tres páginas del informe."""
    documento = canvas.Canvas(str(SALIDA), pagesize=A4)
    documento.setTitle("ORT Recicla: Misión reciclaje")
    documento.setAuthor("Completar nombre del estudiante")
    pagina_inspiracion(documento)
    pagina_flujo(documento)
    pagina_proceso(documento)
    documento.save()


if __name__ == "__main__":
    generar_pdf()