# ORT Recicla: Misión reciclaje

Juego arcade en Python y Pygame. Arrastra cada residuo desde la cinta a su papelera antes de que salga de la pantalla.

## Cómo jugar

- Pulsa **Espacio** o haz clic en **Comenzar**.
- Haz clic sobre un residuo, arrástralo a la papelera correcta y suelta el botón del mouse.
- Pulsa el botón de volumen para silenciar o restaurar los efectos.
- Cada uno de los nueve niveles dura 45 segundos:
	- Nivel 1: 20 elementos a 58 px/s.
	- Nivel 2: 20 elementos a 88 px/s.
	- Nivel 3: 25 elementos a 88 px/s.
	- Nivel 4: 25 elementos a 118 px/s.
	- Nivel 5: 30 elementos a 118 px/s.
	- Nivel 6: 30 elementos a 148 px/s.
	- Nivel 7: 35 elementos a 148 px/s.
	- Nivel 8: 40 elementos a 148 px/s.
	- Nivel 9: 40 elementos a 168 px/s.
- Un residuo mal clasificado, perdido o el tiempo agotado termina el intento. Hay dos reintentos adicionales en el nivel actual.
- Pulsa **Espacio** para continuar y **R** para reintentar. **Esc** cierra el juego.

## Instalación y ejecución

Requiere Python 3 y Pygame:

```powershell
python -m pip install pygame
python main.py
```

El juego dibuja las siluetas con figuras de Pygame y genera los efectos de sonido al iniciar; no necesita imágenes ni audios externos. Para volver a generar el informe, instala `reportlab` y ejecuta `python generar_informe.py`.

## Archivos

- `main.py`: bucle de juego, clase `Residuo`, controles, dibujo y audio.
- `ajustes.py`: colores, dimensiones, duración y velocidades de los niveles.
- `generar_informe.py`: fuente reproducible del informe PDF y del afiche.
- `Informe_ORT_Recicla.pdf`: inspiración, diagrama de flujo, proceso creativo y afiche A4.

## Fuentes y uso de IA

La clasificación sigue la consigna del obligatorio y el programa institucional ORT Recicla. Las cifras de impacto de la portada se tomaron de [Cómo funciona el programa ORT Recicla y qué impacto genera](https://www.ort.edu.uy/la-universidad/sostenibilidad/como-funciona-ort-recicla-y-que-impacto-genera). El código no usa imágenes ni sonidos de terceros: las formas se dibujan en Pygame y los sonidos se sintetizan en tiempo de ejecución.

Se utilizó **GitHub Copilot** como apoyo para idear, implementar y revisar inicialmente el código y la documentación. El estudiante debe revisar y verificar el contenido y declarar el contexto de uso en la entrega.

## Repositorio

Remoto configurado: [Programacion2-99482/Obligatorio1](https://github.com/Programacion2-99482/Obligatorio1). El repositorio local todavía no tiene commits. La consigna pide registrar commits reales, claros y repartidos en el tiempo; no se simularon ni inventaron.

**Antes de entregar:** completa el nombre y número de estudiante en el informe y confirma con el equipo docente el requisito de historial del repositorio.