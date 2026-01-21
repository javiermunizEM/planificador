import os
import json
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import navy
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


# ✅ NUEVAS RUTAS DESDE CONFIG
from config import (
    RUTA_PARAMETROS,
    ruta_textos,
    RUTA_FIRMA,
    RUTA_IMAGENES,
    RUTA_MEDIA,
    ruta_paso,
    ruta_estadisticas,
    BASE_DIR
)

RUTA_SALIDA_PDF = os.path.join(BASE_DIR, "planificador.pdf")



# === FUNCIONES AUXILIARES ===
def cargar_parametros():
    with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_textos():
    with open(ruta_textos(), "r", encoding="utf-8") as f:
        return json.load(f)

def forzar_pagina_impar(pdf):
    """Inserta una página en blanco si estamos en una página par (para que la siguiente sea impar)"""
    if pdf.getPageNumber() % 2 == 0:

        pdf.showPage()

#Creación del pie de página
def agregar_pie_pagina(pdf):
    numero = pdf.getPageNumber()
    textoD = f"{numero} | Escuela de la Memoria"
    textoI = f"Escuela de la Memoria | {numero}"

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.grey)

    if numero % 2 == 0:
        # Página par → alinear a la izquierda
        pdf.drawRightString(19.5 * cm, 1.3 * cm, textoI)
    else:
        # Página impar → alinear a la derecha
        pdf.drawString(2 * cm, 1.3 * cm, textoD)

    pdf.setFillColor(colors.black)



def pagina_como_usar_planificador(pdf, textos):
    pdf.showPage()
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(10.5 * cm, 27 * cm, textos["como_usar_planificador"]["titulo"])

    style = ParagraphStyle(
        "instrucciones",
        fontName="Helvetica",
        fontSize=12,
        leading=18,
        alignment=TA_LEFT,
        spaceAfter=10
    )

    contenido = textos["como_usar_planificador"]["contenido"]
    parrafo = Paragraph(contenido, style)
    parrafo.wrapOn(pdf, 17 * cm, 25 * cm)
    parrafo.drawOn(pdf, 2 * cm, 26 * cm - parrafo.height)

    agregar_pie_pagina(pdf)
    pdf.showPage()

# === SECCIONES DEL PDF ===
def portada(pdf, nombre_alumno):
    pdf.setFont("Helvetica-Bold", 40)
    pdf.drawCentredString(10.5*cm, 22.5*cm, "Planificación")

    pdf.setFont("Helvetica", 40)
    pdf.drawCentredString(10.5*cm, 20.5*cm, nombre_alumno)

    ruta_imagen = os.path.join(RUTA_IMAGENES, "portada.png")
    if os.path.exists(ruta_imagen):
        pdf.drawImage(ruta_imagen, x=3*cm, y=11*cm, width=15*cm, preserveAspectRatio=True)

    pdf.setFont("Helvetica", 30)
    pdf.drawCentredString(10.5*cm, 7.5*cm, "Escuela de la Memoria")

    pdf.showPage()


def pagina_motivacional(pdf, titulo, mensaje, firma_filename):
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(10.5*cm, 26.5*cm, titulo)

    styles = getSampleStyleSheet()
    estilo = styles["Normal"]
    estilo.fontName = "Helvetica"
    estilo.fontSize = 14
    estilo.leading = 18

    mensaje_maquetado = mensaje.replace("\n", "<br/>")
    parrafo = Paragraph(mensaje_maquetado, estilo)
    width, height = parrafo.wrap(15*cm, 10*cm)

    y_inicio = 23.5 * cm  # parte superior donde empieza el párrafo
    parrafo.drawOn(pdf, x=3*cm, y=y_inicio - height)

    firma_path = os.path.join(RUTA_IMAGENES, firma_filename)
    if os.path.exists(firma_path):
        pdf.drawImage(firma_path, 12*cm, 10*cm, width=5*cm, preserveAspectRatio=True)

    agregar_pie_pagina(pdf)
    #pdf.showPage()


def pagina_explicativa(pdf, titulo, contenido):
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(10.5*cm, 26.5*cm, titulo)

    styles = getSampleStyleSheet()
    estilo = styles["Normal"]
    estilo.fontName = "Helvetica"
    estilo.fontSize = 12
    estilo.leading = 16

    parrafo = Paragraph(contenido, estilo)
    width, height = parrafo.wrap(15*cm, 20*cm)

    y_inicio = 23.5 * cm
    parrafo.drawOn(pdf, x=3*cm, y=y_inicio - height)

    agregar_pie_pagina(pdf)
    pdf.showPage()

def portada_mes(pdf, nombre_mes, numero_mes_estudio, ruta_imagen):
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(10.5*cm, 25*cm, nombre_mes.capitalize())

    if os.path.exists(ruta_imagen):
        pdf.drawImage(ruta_imagen, 3*cm, 10*cm, width=15*cm, preserveAspectRatio=True)

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(10.5*cm, 5*cm, f"Mes {numero_mes_estudio}")
    agregar_pie_pagina(pdf)
    pdf.showPage()




def pagina_titulo_con_imagen(pdf, titulo, nombre_imagen):
    pdf.setFont("Helvetica-Bold", 36)
    pdf.drawCentredString(10.5*cm, 20*cm, titulo)

    ruta_imagen = os.path.join(RUTA_IMAGENES, nombre_imagen)
    if os.path.exists(ruta_imagen):
        pdf.drawImage(ruta_imagen, x=3*cm, y=11*cm, width=15*cm, preserveAspectRatio=True)


    pdf.showPage()



def pagina_objetivo(pdf, nombre_alumno):
    pdf.showPage()  # Nueva página
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(10.5*cm, 27*cm, "Mi objetivo")

    style_normal = ParagraphStyle(
        "normal",
        fontName="Helvetica",
        fontSize=12,
        leading=18,
        spaceAfter=10
    )

    preguntas = [
        "¿Por qué quiero aprobar esta oposición?",
        "¿Cómo me voy a sentir cuando lo logre?",
        "¿Cómo cambiará mi vida y la de los demás?",
        "¿Qué impacto positivo causaré en el mundo?"
    ]

    y = 25 * cm
    for pregunta in preguntas:
        p = Paragraph(f"<b>{pregunta}</b>", style_normal)
        p.wrapOn(pdf, 17*cm, 3*cm)
        p.drawOn(pdf, 2*cm, y)
        y -= 1.0 * cm
        for _ in range(3):
            pdf.line(2*cm, y, 19*cm, y)
            y -= 1 * cm
        if pregunta != preguntas[-1]:
            y -= 0.5 * cm  # añade espacio solo entre bloques de pregunta

    y -= 1 * cm
    texto_final = Paragraph(f"<b>Yo, {nombre_alumno}, me comprometo a dar el 100% y a ir a por todas:</b>", style_normal)
    texto_final.wrapOn(pdf, 17*cm, 3*cm)
    texto_final.drawOn(pdf, 2*cm, y)
    y -= 2.5 * cm

    pdf.line(8*cm, y, 18*cm, y)
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(18*cm, y - 0.4*cm, "Firma")

    agregar_pie_pagina(pdf)
    pdf.showPage()


def pagina_una_semana(pdf, semana, frases_motivacionales=None):
    y_inicio = 25 * cm

    numero = semana["semana"]
    dias = semana["dias"]

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(1.5 * cm, y_inicio + 1 * cm, f"Semana {numero}")

    tabla = preparar_tabla(dias)
    w, h = tabla.wrap(18 * cm, 18 * cm)
    tabla.drawOn(pdf, x=1.5 * cm, y=y_inicio - h)

    # Frase motivacional (solo una vez)
    if frases_motivacionales:
        frase = random.choice(frases_motivacionales)
        frases_motivacionales.remove(frase)
        pdf.setFont("Helvetica-Oblique", 12)
        pdf.drawString(1.5 * cm, 2.5 * cm, f"■ {frase}")

    agregar_pie_pagina(pdf)
    pdf.showPage()



def pagina_doble_semana(pdf, semanas, frases_motivacionales):
    y_inicio_superior = 25 * cm
    y_inicio_inferior = 14.2 * cm  # posición vertical de la segunda tabla

    for i in range(0, len(semanas), 2):
        # Semana 1 (arriba)
        semana1 = semanas[i]
        numero1 = semana1["semana"]
        dias1 = semana1["dias"]

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(1.5*cm, y_inicio_superior + 1*cm, f"Semana {numero1}")

        tabla1 = preparar_tabla(dias1)
        w1, h1 = tabla1.wrap(18*cm, 18*cm)
        tabla1.drawOn(pdf, x=1.5*cm, y=y_inicio_superior - h1)

        # Semana 2 (abajo)
        if i + 1 < len(semanas):
            semana2 = semanas[i + 1]
            numero2 = semana2["semana"]
            dias2 = semana2["dias"]

            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(1.5*cm, y_inicio_inferior + 1*cm, f"Semana {numero2}")

            tabla2 = preparar_tabla(dias2)
            w2, h2 = tabla2.wrap(18*cm, 18*cm)
            tabla2.drawOn(pdf, x=1.5*cm, y=y_inicio_inferior - h2)

        # Frase motivacional
        if frases_motivacionales:
            if frases_motivacionales:
                frase = random.choice(frases_motivacionales)
                frases_motivacionales.remove(frase)
                pdf.setFont("Helvetica-Oblique", 12)
                pdf.drawString(1.5*cm, 2.5*cm, f"■ {frase}")
            
            pdf.setFont("Helvetica-Oblique", 12)
            pdf.drawString(1.5*cm, 2.5*cm, f"■ {frase}")
            

        agregar_pie_pagina(pdf)
        pdf.showPage()


def preparar_tabla(dias):
    data = [["Fecha", "Día mes", "Día", "Estudiar", "Repasar"]]
    for dia in dias:
        data.append([
            dia["fecha"],
            dia["dia_mes"],
            dia["dia_semana"],
            dia["estudiar"],
            "\n".join(dia["repasar"]) if dia["repasar"] else "-"
        ])

    tabla = Table(data, colWidths=[3*cm, 2*cm, 3*cm, 5*cm, 5*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',(0, 0),(-1, -1),'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    return tabla


def pagina_titulo_simple(pdf, titulo):
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(10.5*cm, 26*cm, titulo)
    agregar_pie_pagina(pdf)
    pdf.showPage()

def pagina_semana_vacia(pdf, numero_semana, dias, frases_motivacionales=[]):
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(10.5*cm, 27*cm, f"Semana {numero_semana}")

    # === Tabla principal vacía ===
    data = [["Fecha", "Día", "Semana", "Estudiar", "Repasar"]]
    for dia in dias:
        data.append([
            dia["fecha"],
            dia["dia_mes"],
            dia["dia_semana"],
            "",
            ""
        ])


        

    tabla = Table(data, colWidths=[3*cm, 2*cm, 3*cm, 5*cm, 5*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN',(0, 0),(-1, -1),'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    tabla_width, tabla_height = tabla.wrap(18*cm, 18*cm)
    tabla.drawOn(pdf, x=1.5*cm, y=25.5*cm - tabla_height)

    # === Tabla "Mis anotaciones" ===
    anotaciones_data = [["Mis anotaciones"], ["\n" * 10]]
    anotaciones = Table(anotaciones_data, colWidths=[18*cm])
    anotaciones.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.whitesmoke),
        ('ALIGN',(0, 0),(-1, -1),'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    anotaciones.wrapOn(pdf, 18*cm, 8*cm)
    anotaciones.drawOn(pdf, x=1.5*cm, y=13.7*cm)

        # === Tabla de revisión semanal ===
    revision_data = [
        ["Revisión de la semana", ""],
        ["¿Qué funcionó bien?", "\n" * 2],
        ["¿Qué podría mejorar?", "\n" * 2],
        ["¿Cuántas veces cumplí el plan?", "\n" * 2],
        ["¿He dormido al menos 7 horas diarias?", "\n" * 2]
        
    ]

    revision = Table(revision_data, colWidths=[9*cm, 9*cm])
    revision.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN',(0, 0),(-1, -1),'LEFT'),
        ('VALIGN',(0, 0),(-1, -1),'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    revision.wrapOn(pdf, 18*cm, 6*cm)
    revision.drawOn(pdf, x=1.5*cm, y=5.8*cm)


    # === Frase motivacional final ===
    if frases_motivacionales:
        frase = random.choice(frases_motivacionales)
        frases_motivacionales.remove(frase)
        pdf.setFont("Helvetica-Oblique", 12)
        pdf.drawString(1.5*cm, 2.5*cm, f"💬 {frase}")


    agregar_pie_pagina(pdf)
    pdf.showPage()


def pagina_checklist_progreso(pdf, lista_temas):
    temas_por_pagina = 30
    columnas = ["Tema", "Estudiado", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]

    for i in range(0, len(lista_temas), temas_por_pagina):
        bloque = lista_temas[i:i+temas_por_pagina]

        # Título
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawCentredString(10.5*cm, 27*cm, "Progreso del plan")

        # Crear tabla
        data = [columnas]
        for tema in bloque:
            fila = [tema["titulo"]] + [""] * (len(columnas) - 1)
            data.append(fila)

        table = Table(data, colWidths=[7*cm] + [2.2*cm] + [1*cm]*6)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN',(0, 0),(-1, -1),'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))

        # Alinear desde arriba
        table_width, table_height = table.wrap(18*cm, 24*cm)
        table.drawOn(pdf, x=1.5*cm, y=25.5*cm - table_height)

        agregar_pie_pagina(pdf)
        pdf.showPage()




# === EJECUCIÓN PRINCIPAL ===
def ejecutar_paso6():
    parametros = cargar_parametros()
    textos = cargar_textos()
    nombre_alumno = parametros["nombre_alumno"]

    pdf = canvas.Canvas(RUTA_SALIDA_PDF, pagesize=A4)

    # 1. Portada
    portada(pdf, nombre_alumno)

    # 2. Página en blanco
    pdf.showPage()

    # 3. Página motivacional
    motivacional = textos["portada_personal"]
    pagina_motivacional(pdf, motivacional["titulo"], motivacional["mensaje"], motivacional["firma"])

    # 5. Página explicativa
    with open(ruta_textos(), "r", encoding="utf-8") as f:
        textos = json.load(f)
    
    pagina_como_usar_planificador(pdf, textos)
   
    #intro = textos["pagina_inicial"]
    #pagina_explicativa(pdf, intro["titulo"], intro["contenido"])


    # 7. === Página de estadísticas motivacionales ===
    with open(ruta_estadisticas(), "r", encoding="utf-8") as f:
        stats = json.load(f)

    # Leer si el plan es incompleto
    plan_incompleto = False
    try:
        with open("pasos/plan_estado.json", "r", encoding="utf-8") as f:
            plan_estado = json.load(f)
            plan_incompleto = plan_estado.get("plan_incompleto", False)
    except FileNotFoundError:
        pass

    titulo = textos["pagina_estadisticas"]["titulo"]
    contenido = textos["pagina_estadisticas"]["contenido"]

    # Estilo alineado a la izquierda
    style = ParagraphStyle(
        "Estadisticas",
        fontName="Helvetica",
        fontSize=12,
        leading=18,
        alignment=TA_LEFT,
        textColor="black"
    )

    # Frase con valores destacados
    resumen = f"""
    Tienes <b><font color="#0A2754">{stats['dias_restantes']}</font></b> días hasta el examen.<br/>
    Puedes planificar <b><font color="#0A2754">{stats['dias_planificables']}</font></b> días hasta el <b>{(datetime.strptime(parametros['fecha_examen'], "%Y-%m-%d") - timedelta(weeks=2)).strftime("%d-%m-%Y")}</b>.<br/>
    """

    if stats["vueltas_completas"] >= 1:
        resumen += f"""
    Darás <b><font color="#0A2754">{stats['vueltas_completas']}</font></b> vueltas completas a tu temario.<br/>
    La primera vuelta la terminarás el día <b><font color="#0A2754">{stats['fin_primera_vuelta']}</font></b>,
    es decir, dentro de <b><font color="#0A2754">{stats['dias_hasta_fin_primera_vuelta']}</font></b> días desde hoy.<br/>
    """
    else:
        resumen += "<b><font color='red'>⚠️Con esta planificación no llegarás a dar una vuelta completa al temario. ⚠</font></b><br/>"

    resumen += f"""
    Estudiarás <b><font color="#0A2754">{stats['dias_estudio']}</font></b> días y descansarás
    <b><font color="#0A2754">{stats['dias_descanso']}</font></b>.<br/>
    Y en total vas a acumular <b><font color="#0A2754">{stats['tiempo_total']}</font></b> de estudio.<br/><br/>
    <b>¡IMAGINA TODO LO QUE CONSEGUIRÁS EN ESE TIEMPO!</b><br/>
    <b>¡ÁNIMO Y A POR TODAS!</b>
    """

    # Añadir advertencia si el plan es incompleto
    if plan_incompleto:
        resumen += "<br/><br/><b><font color='red'>⚠️ No hay tiempo suficiente para completar ni una vuelta entera al temario. Ajusta tus prioridades o comienza antes.</font></b>"


    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(10.5 * cm, 27 * cm, titulo)

    parrafo = Paragraph(f"{contenido}<br/><br/>{resumen}", style)
    parrafo.wrapOn(pdf, 16 * cm, 25 * cm)
    parrafo.drawOn(pdf, 2 * cm, 24 * cm - parrafo.height)

    agregar_pie_pagina(pdf)
    #pdf.showPage()




    # 8. Contrato y objetivos
    pagina_objetivo(pdf, parametros["nombre_alumno"])

    # Página en blanco
    #pdf.showPage()

    # 9. Portada de la planificación ideal
    pagina_titulo_con_imagen(pdf, "Planificación ideal", "planificacion_ideal.png")

    # === Cargar calendario y frases motivadoras ===
    with open(ruta_paso(5), "r", encoding="utf-8") as f:
        calendario = json.load(f)

    frases = textos.get("frases_motivacionales", [])

    for semana in calendario:
        pagina_una_semana(pdf, semana, frases)

    # === Título para la planificación editable ===
    forzar_pagina_impar(pdf)
    pagina_titulo_con_imagen(pdf, "Mi Planificación", "mi_planificacion.png")

    # Páginas semanales vacías personalizables
    frases_extra = frases.copy()  # reutilizamos pero sin repetir
    for semana in calendario:
        numero = semana["semana"]
        dias = semana["dias"]
        pagina_semana_vacia(pdf, numero, dias, frases_extra)


    # === Portada del resumen de progreso
    forzar_pagina_impar(pdf)
    pagina_titulo_con_imagen(pdf, "¡RECTA FINAL!", "recta_final.png")
    
    # ===========================================================================
    ultima_fecha_str = calendario[-1]["dias"][-1]["fecha"]
    ultima_fecha = datetime.strptime(ultima_fecha_str, "%d-%m-%Y")
    ultima_semana_num = calendario[-1]["semana"]

    DIAS_SEMANA_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    for i in range(2):
        nueva_semana = []
        numero_semana = ultima_semana_num + i + 1

        for j in range(7):
            fecha_actual = ultima_fecha + timedelta(days=(i * 7 + j + 1))
            nueva_semana.append({
                "fecha": fecha_actual.strftime("%d-%m-%Y"),
                "dia_mes": fecha_actual.strftime("%d"),
                "dia_semana": DIAS_SEMANA_ES[fecha_actual.weekday()],
                "estudiar": "",
                "repasar": []
            })

        pagina_semana_vacia(pdf, numero_semana, nueva_semana, frases_extra)
    # ==========================================================================


    # === Página en blanco antes del resumen de progreso
    pdf.showPage()

    # === Portada del resumen de progreso
    forzar_pagina_impar(pdf)
    pagina_titulo_con_imagen(pdf, "El progreso del plan", "progreso_plan.png")


    # === Página de checklist de progreso ===
    with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
        parametros = json.load(f)
    temas = list(parametros["temas"].values())

    pagina_checklist_progreso(pdf, temas)

    # === Última página en blanco
    pdf.showPage()

    # Guardar PDF
    pdf.save()
    print("✅ PDF generado correctamente: planificador.pdf")

# Solo si se ejecuta directamente
if __name__ == "__main__":
    ejecutar_paso6()
