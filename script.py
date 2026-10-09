import os
import re
import json
import time
import requests
import pdfplumber
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# =======================================================================
# 1. CREDENCIALES
# =======================================================================

token_tg = os.getenv("TELEGRAM_TOKEN", "").strip()
chat_id_tg = os.getenv("TELEGRAM_CHAT_ID", "").strip()
groq_key = os.getenv("GROQ_API_KEY", "").strip()

if not all([token_tg, chat_id_tg, groq_key]):
    raise SystemExit(
        "❌ Faltan variables en el entorno. "
        "Verificá TELEGRAM_TOKEN, TELEGRAM_CHAT_ID y GROQ_API_KEY."
    )


# =======================================================================
# 2. ENDPOINTS Y CONFIGURACIÓN
# =======================================================================

url_telegram = f"https://api.telegram.org/bot{token_tg}/sendMessage"
url_groq = "https://api.groq.com/openai/v1/chat/completions"
modelo_groq = "openai/gpt-oss-120b"

url_caba = "https://api-restboletinoficial.buenosaires.gob.ar/obtenerBoletin/{fecha}/true"
url_pba_anteriores = "https://boletinoficial.gba.gob.ar/ediciones-anteriores"
url_pba_pdf = "https://boletinoficial.gba.gob.ar/secciones/{id}/ver"
url_nacion_pdf = "https://s3.arsat.com.ar/cdn-bo-001/pdf-del-dia/primera.pdf"

CAMPOS_REQUERIDOS = ["jurisdiccion", "titulo", "criollo", "letraChica", "articulo", "publicar"]

MAX_NORMAS_POR_JURISDICCION = 3
PAUSA_ENTRE_ANALISIS = 60
PAGINAS_INDICE_CABA = 30
PAGINAS_INDICE_NACION = 10

RUTA_SCRIPT = Path(__file__).resolve().parent
RUTA_DATOS_JS = RUTA_SCRIPT / "datos.js"
RUTA_PDF_CABA = RUTA_SCRIPT / "boletin_caba_temp.pdf"
RUTA_PDF_PBA = RUTA_SCRIPT / "boletin_pba_temp.pdf"
RUTA_PDF_NACION = RUTA_SCRIPT / "boletin_nacion_temp.pdf"


# =======================================================================
# 3. SYSTEM PROMPT
# =======================================================================

SYSTEM_PROMPT = """CONTESTÁ SIEMPRE EN ESPAÑOL DE ARGENTINA. TUTEÁ AL LECTOR.

Sos "IPD - Información para la Defensa", un sistema de análisis jurídico y político que audita diariamente el Boletín Oficial de Nación, PBA y CABA. Tu misión es traducir las normas al lenguaje del pueblo trabajador, desenmascarar el relato oficial y mostrar el entramado de intereses que hay detrás de cada medida.

=======================================================================
I. IDENTIDAD Y ESTILO PERIODÍSTICO
=======================================================================

Analizás desde el Nacional Justicialismo histórico, el Comunitarismo Argentino y la Tercera Posición humanista y cristiana. Tu guía es el "Modelo Argentino para el Proyecto Nacional" (1974) en sus tres dimensiones: Espíritu, Técnica y Comunidad.

Tu estilo narrativo es el del periodismo de investigación crítico: irónico, punzante, con preguntas retóricas y frases explosivas, pero SIEMPRE anclado al texto de la norma. No inventás datos, no fabricás citas. Interpretás y sacás conclusiones, pero no falseás información.

Tu referente estilístico es la claridad expositiva de Perón en sus entrevistas, cruzada con el filo del periodismo de investigación (Lanata, Walsh, Hersh). No sos neutral: tomás partido contra la concentración de poder, los monopolios y la entrega de recursos públicos a manos privadas o multinacionales.

=======================================================================
II. ESTRUCTURA DEL ANÁLISIS
=======================================================================

Cada análisis sigue esta lógica interna (adaptala al formato JSON):

1. LECTURA CRÍTICA: identificá el objeto de la norma, el organismo que la emite y el contexto (privatización, desregulación, concesión, ajuste tarifario, etc.).

2. EL RELATO OFICIAL vs. LA REALIDAD: contrastá lo que la norma DICE que hace con lo que REALMENTE hace. Esta es la clave del análisis. Ejemplo: "El artículo dice que moderniza el Estado, pero en la práctica despide 500 trabajadores y desmantela el área de fiscalización".

3. BENEFICIARIOS DIRECTOS: detectá qué grupos económicos, holdings, multinacionales o personas físicas se benefician. NOMBRALOS con nombre y apellido si están en el texto. Si no están explícitos, inferí a partir de las actividades, concesiones o sectores favorecidos.

4. MECANISMOS DE APROPIACIÓN: explicá cómo se transfiere la renta, los servicios o el dominio. ¿Se elimina un monopolio estatal para crear un oligopolio privado? ¿Se dolarizan tarifas? ¿Se otorgan concesiones sin licitación? ¿Se favorece la autoprestación para que las grandes empresas absorban el negocio?

5. IMPACTO SOCIAL: señalá quiénes pierden (trabajadores, usuarios, pymes, el Estado). Denunciá el costo social y la pérdida de soberanía.

6. LA TRAMPA (LETRA CHICA): identificá el artículo, anexo o derogación donde se esconde la peor parte. Las peores entregas siempre están en los artículos finales o en derogaciones mencionadas al pasar en los considerandos.

REGLA DE ORO: la estructura "dice X, pero en realidad es Y, y la trampa es Z" es la columna vertebral de tu análisis. Aplicala siempre.

=======================================================================
III. CRITERIOS DOCTRINARIOS
=======================================================================

1. TRABAJO Y TRABAJADOR: el sujeto histórico y rector es el trabajador. La justicia social garantiza base material digna. La única política de dignidad social es el pleno empleo productivo, industrial y genuino.

2. PUEBLO, ESTADO Y GOBIERNO: el pueblo existe cuando está organizado (gremios, sindicatos, sociedades de fomento, clubes, mutuales). El Estado es cuerpo orgánico de la Nación. El Gobierno es conducción circunstancial que se inmola por lo permanente (Patria, Nación, Pueblo).

3. INDEPENDENCIA ECONÓMICA Y SOBERANÍA: Estado Empresario Argentino en sectores estratégicos (energía, siderurgia, minería, logística, defensa, electrónica, alimentos, fármacos). Nacionalización del comercio exterior y de depósitos y crédito. Comunidad Capitalizada: difusión universal de la propiedad privada y dignificación del trabajo.

4. ECOLOGISMO COLONIAL: cuando analices vedas, reservas naturales o suspensiones de pesca/minería/energía bajo argumentos ecológicos, evaluá el impacto geopolítico real. Si la restricción frena a la producción y al trabajo nacional pero beneficia de facto la depredación extranjera en los límites fronterizos, denuncialo como "ecologismo colonial" o "entrega pasiva del recurso estratégico".

=======================================================================
IV. TRADUCTOR DE EUFEMISMOS
=======================================================================

- "Modernización / Simplificación del Estado" = reducción de controles públicos, despidos o desmantelamiento de áreas de soberanía.
- "Desregulación / Eficiencia de Mercados" = liberación de tarifas para permitir la usura y el monopolio.
- "Optimización Impositiva / Incentivo a la Inversión" = beneficios fiscales al gran capital extranjero o evasión legalizada.
- "Actualización de Regímenes Laborales" = precarización, quita de convenios, desprotección frente al despido.
- "Articulación Público-Privada" = privatización encubierta o transferencia de rentabilidad estatal a manos privadas.

=======================================================================
V. TONO Y ESTILO
=======================================================================

- Arrancá DIRECTO con el hecho, sin muletillas. NO uses "Mire", "Veamos", "Le explico", "Es así".
- Frases cortas. Explicá lo complejo con metáforas simples (la casa, la familia, el trabajo, el barrio).
- Usá preguntas retóricas: "¿A quién le sirve?", "¿Quién paga?", "¿Qué cambia de verdad?".
- Ironía punzante cuando sume. Pero NUNCA panfletario, nunca agresivo porque sí, nunca académico.
- Frases firmes sin histeria: "perjudica", "recorta", "carga al presupuesto", "no hay garantía".
- NUNCA uses: "podría", "potencialmente", "eventualmente", "es posible que".
- Cerrá con una idea clara y contundente. VARIÁ EL CIERRE entre estas opciones: "Como siempre", "Otra vez sopa", "Y la cuenta la paga el pueblo", "Así estamos". PROHIBIDO repetir el mismo cierre en la misma corrida.

=======================================================================
VI. FORMATO DE RESPUESTA (JSON ESTRICTO)
=======================================================================

Devolvé ÚNICAMENTE un objeto JSON válido, sin texto antes ni después, sin backticks, sin markdown, sin explicaciones.

ESTRUCTURA EXACTA:

{
  "publicar": true | false,
  "jurisdiccion": "nacion" | "pba" | "caba",
  "titulo": "Tipo y número de norma, sin descripción",
  "criollo": "Análisis sintético para alerta. Máximo 500 caracteres.",
  "letraChica": "El dato oculto más importante. Máximo 250 caracteres.",
  "articulo": "Artículo periodístico completo para el blog. Entre 1200 y 1800 caracteres."
}

REGLAS DE CONTENIDO:

- "criollo": MÁXIMO 500 caracteres. Texto plano, un solo párrafo, sin HTML. Aplicá la estructura "dice X, pero en realidad es Y, y la trampa es Z". NOMBRÁ a las empresas o entes concretos si están en el texto. Cerrá con una idea filosa.
- "letraChica": MÁXIMO 250 caracteres. Texto plano, un solo párrafo, sin HTML. Enfocate en el artículo, anexo o derogación donde se esconde la peor parte.
- "articulo": Entre 1200 y 1800 caracteres. Texto plano, sin HTML. Tiene que incluir:
    * Un título llamativo (en la primera línea, separado por un salto de línea).
    * Un copete de una o dos líneas que atrape.
    * El cuerpo del artículo con la estructura "dice/pero/trampa".
    * Un cierre crítico.
  El tono es periodístico de investigación: irónico, punzante, con preguntas retóricas y frases explosivas. Nombralo todo: empresas, organismos, funcionarios si aparecen. Conectá con el impacto sobre el pueblo trabajador.
- "publicar": true si la norma tiene impacto REAL y CONCRETO sobre el pueblo trabajador. false si es administrativa, protocolar, de designación o sin impacto real.
- "jurisdiccion": SIEMPRE en minúscula: "nacion", "pba" o "caba".
- "titulo": SOLO el tipo y número. Ejemplo: "Decreto 512/2026".
- NO uses asteriscos (**), ni guiones bajos (_), ni backticks.

=======================================================================
VII. EJEMPLO DE ANÁLISIS CORRECTO
=======================================================================

Entrada:
Jurisdicción: NACIÓN
Norma: Decreto 512/2026
Sumario: "Se dispone el inicio del proceso de articulación público-privada para la administración de las vías navegables y elevadores portuarios, derogando las restricciones de bandera de la Ley 22.415."

Salida esperada:

{
  "publicar": true,
  "jurisdiccion": "nacion",
  "titulo": "Decreto 512/2026",
  "criollo": "El decreto dice que moderniza la administración de las vías navegables y los elevadores portuarios. Pero en realidad entrega a manos privadas el control del comercio exterior por agua y deroga la restricción de bandera que obligaba a usar barcos argentinos. La trampa: los buques extranjeros podrán operar el cabotaje sin contratar tripulación nacional. ¿A quién le sirve? A los consorcios exportadores. ¿Quién paga? El laburante del puerto y la marina mercante. Otra vez sopa.",
  "letraChica": "La derogación de la Ley 22.415 elimina la reserva de bandera: los buques extranjeros podrán operar el cabotaje y las vías navegables sin obligación de contratar tripulación argentina.",
  "articulo": "Modernización o entrega: el decreto que le regala el río a los exportadores\n\nEl Gobierno presenta el Decreto 512/2026 como una simple modernización administrativa. La realidad es otra: entrega a manos privadas el control de las vías navegables y los elevadores portuarios, y deroga la restricción de bandera que obligaba a usar barcos argentinos.\n\nEl texto dice que busca eficiencia. Pero en la práctica, los consorcios exportadores podrán operar con flotas extranjeras sin pagar costo argentino. La marina mercante nacional pierde su última protección legal. Los laburantes del puerto, sus convenios, sus fuentes de trabajo, quedan a merced de la voluntad empresaria.\n\n¿A quién le sirve? A los grandes exportadores de granos y a los holdings navieros internacionales, que desde ahora manejarán el comercio exterior por agua sin competencia nacional. ¿Quién paga la cuenta? El trabajador argentino. Como siempre."
}

=======================================================================
VIII. VERIFICACIÓN FINAL
=======================================================================

Antes de devolver, verificá:
1. ¿Es JSON válido y parseable?
2. ¿"jurisdiccion" está en minúscula y es una de las tres válidas?
3. ¿"criollo" tiene menos de 500 caracteres y aplica la estructura "dice/pero/trampa"?
4. ¿"letraChica" tiene menos de 250 caracteres?
5. ¿"articulo" tiene entre 1200 y 1800 caracteres y arranca con un título llamativo?
6. ¿"publicar" refleja el impacto real sobre el pueblo trabajador?

Devolvé SOLO el JSON.
"""


# =======================================================================
# 4. PALABRAS CLAVE DEL PRE-FILTRO
# =======================================================================

PALABRAS_INCLUIR = [
    "tarifa", "tarifas", "aumento", "ajuste", "precio", "precios",
    "subsidio", "subsidios", "peaje", "transporte", "colectivo",
    "subte", "tren", "luz", "gas", "agua", "electricidad", "factura",
    "servicio público", "impuesto", "impuestos", "tasa", "tasas",
    "contribución", "contribuciones", "abl", "inmobiliario", "patente",
    "ingresos brutos", "ganancias", "iva", "monotributo",
    "autónomos", "arca", "afip", "exención", "exenciones",
    "alícuota", "alícuotas", "tributo", "tributos",
    "presión fiscal", "evasión", "elusión", "moratoria",
    "plan de pagos", "blanqueo", "recaudación",
    "laboral", "trabajador", "trabajadores", "empleo", "salario",
    "salarios", "convenio", "paritaria", "despido", "indemnización",
    "jubilación", "jubilados", "pensionados", "art", "gremio",
    "sindicato", "industria", "industrial", "industrialización",
    "fábrica", "fábricas", "manufactura", "manufacturero", "producción",
    "productivo", "productiva", "pyme", "pymes", "pequeña empresa",
    "mediana empresa", "emprendedor", "emprendimiento", "cooperativa",
    "mutual", "parque industrial", "polo industrial", "clúster",
    "cadena de valor", "agregado de valor", "sustitución de importaciones",
    "compre nacional", "compre argentino", "desarrollo productivo",
    "fomento", "crédito productivo", "financiamiento productivo", "inti",
    "aduanas", "aduana", "comercio exterior", "importación",
    "exportación", "importaciones", "exportaciones", "arancel",
    "aranceles", "retenciones", "naval", "naviero", "marina mercante",
    "puerto", "puertos", "buque", "buques", "barcos", "flota",
    "astillero", "ferroviario", "ferrocarril", "trenes",
    "vías navegables", "hidrovía", "dragado", "logística", "flete",
    "fletes", "cabotaje", "contenedor", "elevador", "elevadores",
    "pesca", "pesquero", "pesquera", "buque pesquero",
    "flota pesquera", "puerto pesquero", "calamar", "merluza",
    "langostino", "centolla", "corvina", "anchoíta", "milla 201",
    "zona económica exclusiva", "permiso de pesca", "cuota pesquera",
    "veda", "inidep", "astillero pesquero", "conservera",
    "agro", "agropecuario", "agropecuaria", "agrícola", "agricultura",
    "ganadería", "ganadero", "ganadera", "campo", "rural", "chacra",
    "cosecha", "siembra", "cultivo", "cultivos", "grano", "granos",
    "cereal", "cereales", "trigo", "maíz", "soja", "girasol",
    "carne", "carnes", "bovino", "bovinos", "vacuno", "vacunos",
    "porcino", "avícola", "pollo", "leche", "lácteo", "lácteos",
    "tambo", "frigorífico", "matadero", "feedlot", "inta", "senasa",
    "tierra rural", "arrendamiento rural", "semilla", "fertilizante",
    "agroquímico", "forestal", "bosque", "monte",
    "vivienda", "alquiler", "alquileres", "hábitat", "urbano",
    "urbanización", "barrio", "desalojo", "expropiación", "tierra",
    "suelo", "obra pública",
    "salud", "hospital", "medicamento", "obra social", "pami",
    "educación", "escuela", "universidad", "beca", "docente",
    "privatización", "concesión", "licitación", "empresa estatal",
    "regulación", "control", "fiscalización", "soberanía",
    "estratégico", "nacionalización", "defensa", "fuerzas armadas",
    "emergencia", "asistencia social", "ayuda social",
    "subsidio social", "plan social", "comedor", "niñez", "género",
    "violencia",
]

INICIOS_EXCLUIR = [
    "designa", "designación", "nombra", "nombramiento",
    "acepta la renuncia", "renuncia", "cesa", "cese",
    "traslado", "licencia", "sanciona", "prorroga la designación",
    "da de alta", "ratifica", "aprueba compensación de créditos",
    "aprueba modificación presupuestaria", "aprueba gastos de caja chica",
    "aprueba el acta", "otorga licencia", "deja sin efecto",
    "modifica el monto del suplemento",
]

PALABRAS_EXCLUIR = [
    "boletín oficial", "boletin oficial",
]


# =======================================================================
# 5. VALIDAR DICTAMEN
# =======================================================================

def validar_dictamen(dictamen):

    if not isinstance(dictamen, dict):
        return False

    faltantes = [c for c in CAMPOS_REQUERIDOS if c not in dictamen]
    if faltantes:
        print(f"❌ Faltan campos: {faltantes}")
        return False

    for campo in CAMPOS_REQUERIDOS:
        if campo == "publicar":
            continue
        if not dictamen[campo] or not str(dictamen[campo]).strip():
            print(f"❌ Campo '{campo}' vacío.")
            return False

    return True


# =======================================================================
# 6. FUNCIONES PARA CABA
# =======================================================================

def bajar_pdf_boletin_caba():
    """Consulta la API de CABA y baja el PDF del boletín del día."""

    fecha_hoy = datetime.now().strftime("%d-%m-%Y")
    url = url_caba.format(fecha=fecha_hoy)

    print(f"📥 CABA: Consultando API para {fecha_hoy}...")

    try:
        res = requests.get(url, timeout=30)
        print(f"📡 CABA: Código {res.status_code}")

        if res.status_code != 200:
            print("❌ CABA: La API rechazó la solicitud.")
            return None

        data = res.json()
        url_pdf = data.get("boletin", {}).get("url_boletin")

        if not url_pdf:
            print("❌ CABA: No se encontró 'url_boletin'.")
            return None

        print(f"📄 CABA: Bajando PDF...")
        res_pdf = requests.get(url_pdf, timeout=120)

        if res_pdf.status_code != 200:
            print(f"❌ CABA: Error al bajar PDF ({res_pdf.status_code})")
            return None

        with open(RUTA_PDF_CABA, "wb") as f:
            f.write(res_pdf.content)

        tamano_mb = len(res_pdf.content) / 1024 / 1024
        print(f"✅ CABA: PDF bajado ({tamano_mb:.2f} MB)")
        return RUTA_PDF_CABA

    except Exception as e:
        print(f"💥 CABA: Error bajando PDF: {e}")
        return None


def extraer_normas_caba(ruta_pdf):
    """Extrae normas del índice del PDF de CABA."""

    print(f"📖 CABA: Extrayendo índice (primeras {PAGINAS_INDICE_CABA} páginas)...")

    try:
        texto = []
        with pdfplumber.open(ruta_pdf) as pdf:
            limite = min(PAGINAS_INDICE_CABA, len(pdf.pages))
            for i in range(limite):
                pagina = pdf.pages[i].extract_text()
                if pagina:
                    texto.append(pagina)

        texto_completo = "\n".join(texto)
        print(f"✅ CABA: Texto extraído ({len(texto_completo)} caracteres).")

        patron = r'((?:Resolución|Decreto|Ley|Disposición)\s+N°\s+[\w\-/]+)\s*\n(.*?)\.{3,}\s*Pág\.\s*(\d+)'

        normas = []
        for match in re.finditer(patron, texto_completo, re.DOTALL):
            norma = match.group(1).strip()
            sumario = " ".join(match.group(2).strip().split())
            pagina = match.group(3).strip()

            if "de Directorio" in norma:
                continue

            normas.append({
                "norma": norma,
                "sumario": sumario,
                "pagina": pagina
            })

        print(f"✅ CABA: {len(normas)} normas encontradas.")
        return normas

    except Exception as e:
        print(f"💥 CABA: Error extrayendo normas: {e}")
        return []


# =======================================================================
# 7. FUNCIONES PARA PBA
# =======================================================================

def obtener_id_boletin_pba():
    """Scrappea la página de ediciones anteriores y devuelve el ID
    de la sección OFICIAL del boletín de hoy."""

    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    print(f"📥 PBA: Buscando boletín del {fecha_hoy}...")

    try:
        res = requests.get(url_pba_anteriores, timeout=30)
        print(f"📡 PBA: Código {res.status_code}")

        if res.status_code != 200:
            print("❌ PBA: La página rechazó la solicitud.")
            return None

        html = res.text
        indice_fecha = html.find(f"- {fecha_hoy}")

        if indice_fecha == -1:
            print(f"❌ PBA: No se encontró el boletín del {fecha_hoy}.")
            return None

        bloque = html[indice_fecha:indice_fecha + 5000]
        match = re.search(r'/secciones/(\d+)/ver', bloque)

        if not match:
            print("❌ PBA: No se encontró el ID de la sección OFICIAL.")
            return None

        id_boletin = match.group(1)
        print(f"✅ PBA: ID del boletín OFICIAL = {id_boletin}")
        return id_boletin

    except Exception as e:
        print(f"💥 PBA: Error buscando ID: {e}")
        return None


def bajar_pdf_boletin_pba(id_boletin):
    """Baja el PDF del boletín de PBA."""

    if not id_boletin:
        return None

    url = url_pba_pdf.format(id=id_boletin)
    print(f"📄 PBA: Bajando PDF desde {url}...")

    try:
        res = requests.get(url, timeout=180)

        if res.status_code != 200:
            print(f"❌ PBA: Error al bajar PDF ({res.status_code})")
            return None

        with open(RUTA_PDF_PBA, "wb") as f:
            f.write(res.content)

        tamano_mb = len(res.content) / 1024 / 1024
        print(f"✅ PBA: PDF bajado ({tamano_mb:.2f} MB)")
        return RUTA_PDF_PBA

    except Exception as e:
        print(f"💥 PBA: Error bajando PDF: {e}")
        return None


def extraer_normas_pba(ruta_pdf):
    """Extrae normas del PDF completo de PBA."""

    print("📖 PBA: Extrayendo texto del PDF completo...")

    try:
        texto = []
        with pdfplumber.open(ruta_pdf) as pdf:
            total = len(pdf.pages)
            print(f"📄 PBA: {total} páginas para procesar.")

            for pagina in pdf.pages:
                contenido = pagina.extract_text()
                if contenido:
                    texto.append(contenido)

        texto_completo = "\n".join(texto)
        print(f"✅ PBA: Texto extraído ({len(texto_completo)} caracteres).")

        patron_norma = r'((?:DECRETO|RESOLUCIÓN|DISPOSICIÓN)\s+N°\s+[\d\-A-Za-z/]+)'
        matches = list(re.finditer(patron_norma, texto_completo, re.IGNORECASE))

        normas = []
        for i, match in enumerate(matches):
            inicio = match.start()
            fin = matches[i + 1].start() if i + 1 < len(matches) else len(texto_completo)

            titulo = match.group(1).strip()
            texto_norma = texto_completo[inicio:fin].strip()
            texto_norma_limpio = " ".join(texto_norma.split())[:3000]

            if len(texto_norma_limpio) < 200:
                continue

            normas.append({
                "norma": titulo,
                "sumario": texto_norma_limpio,
                "pagina": ""
            })

        print(f"✅ PBA: {len(normas)} normas encontradas.")
        return normas

    except Exception as e:
        print(f"💥 PBA: Error extrayendo normas: {e}")
        return []


# =======================================================================
# 8. FUNCIONES PARA NACIÓN
# =======================================================================

def bajar_pdf_boletin_nacion():
    """Baja el PDF de la primera sección del Boletín Oficial de Nación."""

    print(f"📄 NACIÓN: Bajando PDF desde {url_nacion_pdf}...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        res = requests.get(url_nacion_pdf, headers=headers, timeout=180)

        if res.status_code != 200:
            print(f"❌ NACIÓN: Error al bajar PDF ({res.status_code})")
            return None

        with open(RUTA_PDF_NACION, "wb") as f:
            f.write(res.content)

        tamano_mb = len(res.content) / 1024 / 1024
        print(f"✅ NACIÓN: PDF bajado ({tamano_mb:.2f} MB)")
        return RUTA_PDF_NACION

    except Exception as e:
        print(f"💥 NACIÓN: Error bajando PDF: {e}")
        return None


def extraer_normas_nacion(ruta_pdf):
    """Extrae normas del índice del PDF de Nación."""

    print(f"📖 NACIÓN: Extrayendo índice (primeras {PAGINAS_INDICE_NACION} páginas)...")

    try:
        texto = []
        with pdfplumber.open(ruta_pdf) as pdf:
            limite = min(PAGINAS_INDICE_NACION, len(pdf.pages))
            for i in range(limite):
                pagina = pdf.pages[i].extract_text()
                if pagina:
                    texto.append(pagina)

        texto_completo = "\n".join(texto)
        print(f"✅ NACIÓN: Texto extraído ({len(texto_completo)} caracteres).")

        patron = r'([^\.]+?)\.\s+((?:Decreto|Resolución(?:\s+General)?|Disposición)\s+\d+/\d{4})\.\s*([A-Z]+-\d+-[\w\-#\-]+)?\s*[-.]?\s*(.*?)\.{1,}\s*(\d+)(?=\s*(?:[A-ZÁÉÍÓÚÑ]|$))'

        normas = []
        for match in re.finditer(patron, texto_completo, re.DOTALL):
            organismo = match.group(1).strip()
            norma = match.group(2).strip()
            codigo = match.group(3).strip() if match.group(3) else ""
            sumario = " ".join(match.group(4).split()).strip() if match.group(4) else ""
            pagina = match.group(5).strip()

            sumario_completo = f"{organismo}. {sumario}".strip()

            normas.append({
                "norma": norma,
                "sumario": sumario_completo,
                "pagina": pagina
            })

        print(f"✅ NACIÓN: {len(normas)} normas encontradas.")
        return normas

    except Exception as e:
        print(f"💥 NACIÓN: Error extrayendo normas: {e}")
        return []


# =======================================================================
# 9. FILTRAR NORMAS RELEVANTES
# =======================================================================

def filtrar_normas_relevantes(normas):
    """Aplica el filtro por palabras clave."""

    print(f"🎯 IPD: Filtrando {len(normas)} normas...")

    candidatas = []

    for norma in normas:
        sumario = norma.get("sumario", "").lower().strip()
        norma_str = norma.get("norma", "").lower()
        texto = f"{sumario} {norma_str}"

        if any(sumario.startswith(p) for p in INICIOS_EXCLUIR):
            continue

        if any(p in texto for p in PALABRAS_EXCLUIR):
            continue

        matches = sum(1 for p in PALABRAS_INCLUIR if p in texto)

        if matches == 0:
            continue

        candidatas.append({**norma, "matches": matches})

    candidatas.sort(key=lambda x: x["matches"], reverse=True)
    top = candidatas[:MAX_NORMAS_POR_JURISDICCION]

    print(f"✅ {len(top)} normas pasaron el filtro (de {len(normas)}).")
    return top


# =======================================================================
# 10. CONSULTAR GROQ (con retry inteligente)
# =======================================================================

def consultar_groq(norma, jurisdiccion, max_reintentos=3):
    """Analiza una norma con Groq. Maneja rate limit (429) y JSON inválido
    con reintentos automáticos."""

    titulo = norma.get("norma", "Sin título")
    print(f"🤖 Groq: Analizando '{titulo}'...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_key}"
    }

    pagina_norma = norma.get("pagina", "") or "N/D"

    norma_texto = (
        "## NORMA A ANALIZAR\n\n"
        f"Jurisdicción: {jurisdiccion.upper()}\n"
        f"Tipo y número: {norma.get('norma', '')}\n"
        f"Fecha de análisis: {datetime.now().strftime('%d/%m/%Y')}\n"
        f"Página del boletín: {pagina_norma}\n"
        f"Sumario oficial:\n{norma.get('sumario', '')}\n\n"
        "Analizá esta norma siguiendo el formato JSON del system prompt."
    )

    payload_groq = {
        "model": modelo_groq,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": norma_texto}
        ],
        "temperature": 0.4,
        "max_tokens": 2000,
        "frequency_penalty": 0.3,
        "response_format": {"type": "json_object"}
    }

    for intento in range(1, max_reintentos + 1):
        try:
            res_groq = requests.post(
                url_groq, headers=headers, json=payload_groq, timeout=120
            )
            print(f"📡 Groq: Código {res_groq.status_code} (intento {intento}/{max_reintentos})")

            # CASO 1: RATE LIMIT (429)
            if res_groq.status_code == 429:
                espera = 30
                try:
                    error_data = res_groq.json()
                    mensaje = error_data.get("error", {}).get("message", "")
                    match = re.search(r"try again in ([\d.]+)s", mensaje)
                    if match:
                        espera = float(match.group(1)) + 5
                except Exception:
                    pass

                print(f"⏸️ Rate limit. Esperando {espera:.1f}s antes de reintentar...")
                time.sleep(espera)
                continue

            # CASO 2: OTROS ERRORES HTTP
            if res_groq.status_code != 200:
                print(f"❌ Groq rechazó la solicitud ({res_groq.status_code}).")
                print(res_groq.text[:300])
                if intento < max_reintentos:
                    print(f"⏸️ Reintentando en 15s...")
                    time.sleep(15)
                    continue
                return None

            # CASO 3: RESPUESTA OK → parsear
            data = res_groq.json()

            try:
                contenido = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError):
                print("❌ Estructura inesperada en Groq.")
                if intento < max_reintentos:
                    print("⏸️ Reintentando en 15s...")
                    time.sleep(15)
                    continue
                return None

            try:
                dictamen = json.loads(contenido)
            except json.JSONDecodeError as e:
                print(f"❌ JSON inválido: {e}")
                print(contenido[:300])
                if intento < max_reintentos:
                    print("⏸️ Reintentando en 15s...")
                    time.sleep(15)
                    continue
                return None

            # CASO 4: JSON OK pero con campos vacíos → reintentar
            if not validar_dictamen(dictamen):
                print(f"⚠️ Dictamen incompleto en intento {intento}/{max_reintentos}.")
                if intento < max_reintentos:
                    print("⏸️ Reintentando en 15s...")
                    time.sleep(15)
                    continue
                return None

            print(f"⚖️ Dictamen válido (intento {intento}/{max_reintentos}).")
            return dictamen

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout en intento {intento}/{max_reintentos}.")
            if intento < max_reintentos:
                time.sleep(15)
                continue
            return None

        except Exception as e:
            print(f"💥 Error con Groq: {e}")
            if intento < max_reintentos:
                time.sleep(15)
                continue
            return None

    print(f"❌ Se agotaron los {max_reintentos} intentos para '{titulo}'.")
    return None
# =======================================================================
# 11. ESCAPAR HTML
# =======================================================================

def escapar_html(texto):

    if not texto:
        return ""

    texto = texto.replace("<b>", "___B_OPEN___")
    texto = texto.replace("</b>", "___B_CLOSE___")

    texto = texto.replace("&", "&amp;")
    texto = texto.replace("<", "&lt;")
    texto = texto.replace(">", "&gt;")

    texto = texto.replace("___B_OPEN___", "<b>")
    texto = texto.replace("___B_CLOSE___", "</b>")

    return texto


# =======================================================================
# 12. FORMATEAR PARA TELEGRAM
# =======================================================================

def formatear_para_telegram(dictamen):

    jurisdiccion = str(dictamen.get("jurisdiccion", "")).upper()
    titulo = escapar_html(dictamen.get("titulo", ""))
    criollo = escapar_html(dictamen.get("criollo", ""))
    letra_chica = escapar_html(dictamen.get("letraChica", ""))

    # Traducir jurisdicción
    nombres_jur = {
        "NACION": "Gobierno Nacional",
        "PBA": "Provincia de Buenos Aires",
        "CABA": "Ciudad Autónoma de Buenos Aires"
    }
    jurisdiccion_completa = nombres_jur.get(jurisdiccion, jurisdiccion)

    mensaje = (
        "<b>📢 IPD: Actualización de Boletines Oficiales</b>\n\n"
        f"<b>🏛️ {jurisdiccion_completa}</b>\n"
        f"<b>📋 {titulo}</b>\n\n"
        f"{criollo}\n\n"
        f"<b>📝 La Letra Chica:</b>\n{letra_chica}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 Sumate a la comunidad:\n"
        '<a href="https://ipdboletin.github.io">ipdboletin.github.io</a>'
    )

    return mensaje


# =======================================================================
# 13. ENVIAR A TELEGRAM
# =======================================================================

def enviar_telegram(mensaje):

    payload_tg = {
        "chat_id": chat_id_tg,
        "text": mensaje,
        "parse_mode": "HTML"
    }

    for intento in range(2):
        try:
            res = requests.post(url_telegram, json=payload_tg, timeout=60)
            if res.status_code == 200:
                print("🚀 Telegram OK")
                return True
            print(f"❌ Telegram rechazó ({res.status_code})")
            print(res.text[:300])
            return False
        except Exception as e:
            if intento == 0:
                print(f"⚠️ Timeout, reintentando en 5s...")
                time.sleep(5)
            else:
                print(f"💥 Error Telegram (2 intentos): {e}")
                return False


# =======================================================================
# 14. GUARDAR EN datos.js
# =======================================================================

def ya_existe_en_datos(titulo):
    if not RUTA_DATOS_JS.exists():
        return False
    with open(RUTA_DATOS_JS, "r", encoding="utf-8") as f:
        contenido = f.read()
    titulo_escapado = titulo.replace('"', '\\"')
    return f'titulo: "{titulo_escapado}"' in contenido


def construir_entrada_js(dictamen, fecha):

    def limpiar(valor):
        valor = str(valor).strip()
        valor = valor.replace("\\", "\\\\")
        valor = valor.replace('"', '\\"')
        valor = valor.replace("\n", "\\n")
        valor = valor.replace("\r", "")
        return valor

    return (
        "  {\n"
        f'    fecha: "{fecha}",\n'
        f'    jurisdiccion: "{limpiar(dictamen["jurisdiccion"])}",\n'
        f'    titulo: "{limpiar(dictamen["titulo"])}",\n'
        f'    criollo: "{limpiar(dictamen["criollo"])}",\n'
        f'    letraChica: "{limpiar(dictamen["letraChica"])}",\n'
        f'    articulo: "{limpiar(dictamen["articulo"])}"\n'
        "  },\n"
    )


def guardar_en_datos_js(dictamen):

    titulo = dictamen.get("titulo", "").strip()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    if ya_existe_en_datos(titulo):
        print(f"⚠️ Ya existe '{titulo}'. No se agrega.")
        return False

    if not RUTA_DATOS_JS.exists():
        print(f"❌ No se encontró {RUTA_DATOS_JS}.")
        return False

    try:
        with open(RUTA_DATOS_JS, "r", encoding="utf-8") as f:
            contenido = f.read()

        marcador = "const baseDatosIPD = ["
        indice = contenido.find(marcador)

        if indice == -1:
            print("❌ No se encontró el marcador en datos.js.")
            return False

        punto = indice + len(marcador) + 1
        nueva = construir_entrada_js(dictamen, fecha_hoy)

        nuevo = contenido[:punto] + nueva + contenido[punto:]

        with open(RUTA_DATOS_JS, "w", encoding="utf-8") as f:
            f.write(nuevo)

        print(f"✅ '{titulo}' agregada a datos.js.")
        return True

    except Exception as e:
        print(f"💥 Error guardando: {e}")
        return False


# =======================================================================
# 15. PROCESAR UNA JURISDICCIÓN
# =======================================================================

def procesar_jurisdiccion(jurisdiccion):
    """Procesa CABA, PBA o Nación. Devuelve lista de resultados."""

    print(f"\n{'═' * 70}")
    print(f"🗺️ PROCESANDO {jurisdiccion.upper()}")
    print(f"{'═' * 70}\n")

    if jurisdiccion == "caba":
        ruta_pdf = bajar_pdf_boletin_caba()
        normas = extraer_normas_caba(ruta_pdf) if ruta_pdf else []
    elif jurisdiccion == "pba":
        id_boletin = obtener_id_boletin_pba()
        ruta_pdf = bajar_pdf_boletin_pba(id_boletin) if id_boletin else None
        normas = extraer_normas_pba(ruta_pdf) if ruta_pdf else []
    elif jurisdiccion == "nacion":
        ruta_pdf = bajar_pdf_boletin_nacion()
        normas = extraer_normas_nacion(ruta_pdf) if ruta_pdf else []
    else:
        print(f"❌ Jurisdicción desconocida: {jurisdiccion}")
        return []

    if not normas:
        print(f"⚠️ No se encontraron normas en {jurisdiccion.upper()}.")
        return []

    candidatas = filtrar_normas_relevantes(normas)

    if not candidatas:
        print(f"⚠️ Ninguna norma de {jurisdiccion.upper()} pasó el filtro.")
        return []

    print(f"\n🎯 Analizando {len(candidatas)} normas de {jurisdiccion.upper()}...\n")

    resultados = []

    for i, norma in enumerate(candidatas, 1):
        print(f"\n{'─' * 70}")
        print(f"📋 [{jurisdiccion.upper()}] NORMA {i}/{len(candidatas)}: {norma.get('norma', '')}")
        print(f"{'─' * 70}\n")

        dictamen = consultar_groq(norma, jurisdiccion)

        if not dictamen:
            print(f"⚠️ No se pudo analizar. Se saltea.")
            continue

        if not dictamen.get("publicar", False):
            print(f"⏭️ Groq: no amerita publicar.")
            continue

        mensaje = formatear_para_telegram(dictamen)
        enviado = enviar_telegram(mensaje)
        guardado = guardar_en_datos_js(dictamen)

        resultados.append({
            "titulo": dictamen.get("titulo", ""),
            "telegram": enviado,
            "datos_js": guardado
        })

        if i < len(candidatas):
            print(f"\n⏸️ Pausa de {PAUSA_ENTRE_ANALISIS}s...\n")
            time.sleep(PAUSA_ENTRE_ANALISIS)

    return resultados


# =======================================================================
# 16. PROCESO PRINCIPAL
# =======================================================================

def ejecutar_patrullaje():

    print("")
    print("=" * 70)
    print("🛡️ IPD - INFORMACIÓN PARA LA DEFENSA")
    print("🕵️ Iniciando patrullaje...")
    print("=" * 70)

    todos = {}

    todos["caba"] = procesar_jurisdiccion("caba")
    todos["pba"] = procesar_jurisdiccion("pba")
    todos["nacion"] = procesar_jurisdiccion("nacion")

    print("\n")
    print("=" * 70)
    print("📊 RESUMEN DEL PATRULLAJE")
    print("=" * 70)

    for jur, resultados in todos.items():
        print(f"\n  {jur.upper()}: {len(resultados)} publicadas")
        for r in resultados:
            tg = "✅" if r["telegram"] else "❌"
            js = "✅" if r["datos_js"] else "❌"
            print(f"    - {r['titulo']} | TG: {tg} | JS: {js}")

    print("\n" + "=" * 70)
    print("")


# =======================================================================
# 17. EJECUTAR
# =======================================================================

if __name__ == "__main__":
    ejecutar_patrullaje()
