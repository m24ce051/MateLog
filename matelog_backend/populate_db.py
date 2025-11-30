"""
Script para poblar la base de datos con datos de prueba.
Ejecutar con: python manage.py shell < populate_db.py
"""

from lessons.models import Leccion, Tema, ContenidoTema, Ejercicio, OpcionMultiple

print("🚀 Iniciando población de base de datos...")

# Limpiar datos existentes (opcional)
print("📝 Limpiando datos existentes...")
OpcionMultiple.objects.all().delete()
Ejercicio.objects.all().delete()
ContenidoTema.objects.all().delete()
Tema.objects.all().delete()
Leccion.objects.all().delete()

# ========== LECCIÓN 1: Introducción a la Lógica ==========
print("📚 Creando Lección 1: Introducción a la Lógica...")

leccion1 = Leccion.objects.create(
    orden=1,
    titulo="Introducción a la Lógica Matemática",
    descripcion="Conceptos fundamentales de lógica proposicional y razonamiento lógico.",
    is_active=True
)

# --- Tema 1.1: Proposiciones ---
tema1_1 = Tema.objects.create(
    leccion=leccion1,
    orden=1,
    titulo="Proposiciones Lógicas",
    descripcion="¿Qué son las proposiciones y cómo identificarlas?",
    is_active=True
)

# Contenido del Tema 1.1
ContenidoTema.objects.create(
    tema=tema1_1,
    orden=1,
    tipo='TEORIA',
    contenido_texto="<h3>¿Qué es una Proposición?</h3><p>Una <b>proposición</b> es una oración declarativa que puede ser verdadera o falsa, pero no ambas. Por ejemplo:</p><ul><li>\"El cielo es azul\" (puede ser verdadera o falsa)</li><li>\"2 + 2 = 4\" (verdadera)</li><li>\"5 es mayor que 10\" (falsa)</li></ul>"
)

ContenidoTema.objects.create(
    tema=tema1_1,
    orden=2,
    tipo='EJEMPLO',
    contenido_texto="<h3>Ejemplo 1</h3><p>Analicemos: \"El agua hierve a 100°C al nivel del mar\"</p><p>Esta es una <b>proposición</b> porque:</p><ol><li>Es una oración declarativa</li><li>Tiene un valor de verdad definido (verdadero)</li><li>No es ambigua</li></ol>"
)

ContenidoTema.objects.create(
    tema=tema1_1,
    orden=3,
    tipo='EJEMPLO_EXTRA',
    contenido_texto="<h3>Ejemplo Extra: No Proposiciones</h3><p>Las siguientes NO son proposiciones:</p><ul><li>\"¿Qué hora es?\" (pregunta)</li><li>\"¡Cierra la puerta!\" (orden)</li><li>\"x + 5 = 10\" (contiene variable sin valor asignado)</li></ul>"
)

ContenidoTema.objects.create(
    tema=tema1_1,
    orden=4,
    tipo='TEORIA',
    contenido_texto="<h3>Notación</h3><p>Las proposiciones se representan con letras minúsculas:</p><ul><li>p: \"Llueve\"</li><li>q: \"Hace frío\"</li><li>r: \"Es lunes\"</li></ul>"
)

# Ejercicios del Tema 1.1
ejercicio1 = Ejercicio.objects.create(
    tema=tema1_1,
    orden=1,
    tipo='MULTIPLE',
    dificultad='FACIL',
    instruccion='Selecciona la opción correcta',
    enunciado='¿Cuál de las siguientes es una proposición?',
    respuesta_correcta='B',
    texto_ayuda='Recuerda: una proposición debe tener un valor de verdad claro.',
    retroalimentacion_correcta='¡Correcto! Es una oración declarativa con valor de verdad.',
    retroalimentacion_incorrecta='Incorrecto. Revisa la definición de proposición.'
)

OpcionMultiple.objects.create(ejercicio=ejercicio1, letra='A', texto='¿Dónde vives?')
OpcionMultiple.objects.create(ejercicio=ejercicio1, letra='B', texto='La Luna orbita la Tierra')
OpcionMultiple.objects.create(ejercicio=ejercicio1, letra='C', texto='¡Qué hermoso día!')
OpcionMultiple.objects.create(ejercicio=ejercicio1, letra='D', texto='x > 5')

ejercicio2 = Ejercicio.objects.create(
    tema=tema1_1,
    orden=2,
    tipo='ABIERTO',
    dificultad='FACIL',
    instruccion='Responde con "verdadero" o "falso"',
    enunciado='¿Es "Haz tu tarea" una proposición?',
    respuesta_correcta='falso',
    texto_ayuda='Las órdenes o mandatos no son proposiciones.',
    retroalimentacion_incorrecta='Las órdenes no tienen valor de verdad, por lo tanto no son proposiciones.'
)

# Agregar más ejercicios para completar ~15
for i in range(3, 16):
    Ejercicio.objects.create(
        tema=tema1_1,
        orden=i,
        tipo='MULTIPLE' if i % 2 == 0 else 'ABIERTO',
        dificultad='FACIL' if i < 8 else 'INTERMEDIO' if i < 13 else 'DIFICIL',
        instruccion='Responde correctamente',
        enunciado=f'Ejercicio de práctica número {i}',
        respuesta_correcta='A' if i % 2 == 0 else 'verdadero',
        texto_ayuda=f'Pista para el ejercicio {i}'
    )
    
    if i % 2 == 0:
        ej = Ejercicio.objects.get(tema=tema1_1, orden=i)
        OpcionMultiple.objects.create(ejercicio=ej, letra='A', texto='Opción correcta')
        OpcionMultiple.objects.create(ejercicio=ej, letra='B', texto='Opción incorrecta 1')
        OpcionMultiple.objects.create(ejercicio=ej, letra='C', texto='Opción incorrecta 2')

print(f"  ✓ Tema 1.1 creado con {tema1_1.ejercicios.count()} ejercicios")

# --- Tema 1.2: Conectivos Lógicos ---
tema1_2 = Tema.objects.create(
    leccion=leccion1,
    orden=2,
    titulo="Conectivos Lógicos",
    descripcion="Operadores que combinan proposiciones: Y, O, NO",
    is_active=True
)

ContenidoTema.objects.create(
    tema=tema1_2,
    orden=1,
    tipo='TEORIA',
    contenido_texto="<h3>Conectivos Lógicos</h3><p>Los <b>conectivos lógicos</b> nos permiten combinar proposiciones simples para formar proposiciones compuestas:</p><ul><li><b>Conjunción (Y):</b> p ∧ q</li><li><b>Disyunción (O):</b> p ∨ q</li><li><b>Negación (NO):</b> ¬p</li></ul>"
)

ContenidoTema.objects.create(
    tema=tema1_2,
    orden=2,
    tipo='EJEMPLO',
    contenido_texto="<h3>Ejemplo: Conjunción</h3><p>Sean:</p><ul><li>p: \"Llueve\"</li><li>q: \"Hace frío\"</li></ul><p>Entonces p ∧ q significa: \"Llueve Y hace frío\"</p><p>Es verdadero solo cuando AMBAS proposiciones son verdaderas.</p>"
)

# Agregar ejercicios para el tema 1.2
for i in range(1, 16):
    Ejercicio.objects.create(
        tema=tema1_2,
        orden=i,
        tipo='MULTIPLE' if i % 3 == 0 else 'ABIERTO',
        dificultad='FACIL' if i < 6 else 'INTERMEDIO' if i < 11 else 'DIFICIL',
        instruccion='Responde correctamente',
        enunciado=f'Ejercicio sobre conectivos lógicos #{i}',
        respuesta_correcta='A' if i % 3 == 0 else 'verdadero',
        texto_ayuda=f'Recuerda las tablas de verdad'
    )

print(f"  ✓ Tema 1.2 creado con {tema1_2.ejercicios.count()} ejercicios")

# ========== LECCIÓN 2: Tablas de Verdad ==========
print("📚 Creando Lección 2: Tablas de Verdad...")

leccion2 = Leccion.objects.create(
    orden=2,
    titulo="Tablas de Verdad",
    descripcion="Construcción y análisis de tablas de verdad.",
    is_active=True
)

tema2_1 = Tema.objects.create(
    leccion=leccion2,
    orden=1,
    titulo="Introducción a Tablas de Verdad",
    descripcion="¿Qué son y cómo construirlas?",
    is_active=True
)

ContenidoTema.objects.create(
    tema=tema2_1,
    orden=1,
    tipo='TEORIA',
    contenido_texto="<h3>Tablas de Verdad</h3><p>Una <b>tabla de verdad</b> muestra todos los posibles valores de verdad de una proposición compuesta.</p>"
)

# Agregar ejercicios
for i in range(1, 16):
    Ejercicio.objects.create(
        tema=tema2_1,
        orden=i,
        tipo='MULTIPLE' if i % 2 == 0 else 'ABIERTO',
        dificultad='INTERMEDIO',
        instruccion='Completa la tabla de verdad',
        enunciado=f'Ejercicio de tabla de verdad #{i}',
        respuesta_correcta='B' if i % 2 == 0 else 'falso'
    )

print(f"  ✓ Tema 2.1 creado con {tema2_1.ejercicios.count()} ejercicios")

print("\n✅ ¡Base de datos poblada exitosamente!")
print(f"📊 Resumen:")
print(f"  - Lecciones: {Leccion.objects.count()}")
print(f"  - Temas: {Tema.objects.count()}")
print(f"  - Contenidos: {ContenidoTema.objects.count()}")
print(f"  - Ejercicios: {Ejercicio.objects.count()}")
print(f"  - Opciones: {OpcionMultiple.objects.count()}")
