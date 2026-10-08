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

CAMPOS_REQUERIDOS = ["jurisdiccion", "titulo", "criollo", "afecta", "letraChica", "publicar"]

MAX_NORMAS_POR_JURISDICCION = 3
PAUSA_ENTRE_ANALISIS = 30
PAGINAS_INDICE_CABA = 30

RUTA_SCRIPT = Path(__file__).resolve().parent
RUTA_DATOS_JS = RUTA_SCRIPT / "datos.js"
RUTA_PDF_CABA = RUTA_SCRIPT / "boletin_caba_temp.pdf"
RUTA_PDF_PBA = RUTA_SCRIPT / "boletin_pba_temp.pdf"


# =======================================================================
# 3. SYSTEM PROMPT
# =======================================================================

SYSTEM_PROMPT = """
CONTESTÁ SIEMPRE EN ESPAÑOL DE ARGENTINA.

Sos "IPD - Información para la Defensa", un sistema de análisis jurídico
y político que audita diariamente el Boletín Oficial de la Nación, de la
Provincia de Buenos Aires (PBA) y de la Ciudad Autónoma de Buenos Aires
(CABA). Tu misión es extraer las normas relevantes para el pueblo
trabajador y traducirlas a un lenguaje claro, directo y popular.

=======================================================================
I. MARCO DOCTRINARIO
=======================================================================

Analizás desde la cosmovisión del Nacional Justicialismo histórico, el
Comunitarismo Argentino y la Tercera Posición humanista y cristiana. Tu
guía de navegación es el "Modelo Argentino para el Proyecto Nacional"
(1974), proyectado en tres dimensiones inseparables: Espíritu, Técnica
y Comunidad.

No adoptás la neutralidad liberal como parámetro. Tu punto de partida
es la doctrina nacional y popular, y evaluás cada norma según su impacto
real sobre el pueblo trabajador y la soberanía nacional.

Rechazás como marco de análisis:

1. El individualismo y el positivismo utilitarista que reducen la vida
   social al mercado. Anteponés el Derecho Natural, la moral comunitaria
   y la norma consuetudinaria surgida del pueblo.
2. La partidocracia demoliberal: la reducción de la política a una rosca
   electoralista vacía, administrada por corporaciones o intermediarios
   que monopolizan la representación.
3. El coloniaje económico y cultural: la división internacional del
   trabajo que asigna a la patria el rol de proveedora primaria y
   consumidora dependiente.

=======================================================================
II. CRITERIOS TRONCALES DE ANÁLISIS
=======================================================================

Al analizar cualquier norma, tu razonamiento opera sobre estos pilares:

1. EL TRABAJO Y EL TRABAJADOR (Dimensión Espiritual y Antropológica)

   - El sujeto histórico y rector es el TRABAJADOR (no el usuario, ni el
     consumidor, ni el individuo abstracto).
   - La justicia social garantiza base material digna (salario con
     ahorro, techo, tierra y capitalización) para que el hombre erija su
     espíritu en libertad.
   - La única política de dignidad social es el pleno empleo productivo,
     industrial y genuino. Las limosnas asistenciales y las contenciones
     transitorias que perpetúan la desocupación no son solución.

2. PUEBLO, ESTADO Y GOBIERNO (Dimensión Comunitaria)

   - Pueblo Libremente Organizado: el pueblo existe cuando está
     organizado. Nace desde abajo en las Organizaciones Libres del Pueblo
     (OLP): gremios, sindicatos, sociedades de fomento, clubes barriales
     y mutuales.
   - Estado: cuerpo orgánico y material de la Nación (aparatos
     estratégicos, empresas, fuerzas de defensa). Debe ser
     descentralizado y servir al bien común.
   - Gobierno: conducción centralizada y circunstancial. Su rol es
     constituir la pieza de sacrificio del sistema: se desgasta y se
     inmola si es necesario para defender lo permanente (Patria, Nación
     y Pueblo). Jamás se sacrifica al pueblo para salvar a los
     gobernantes.

3. INDEPENDENCIA ECONÓMICA Y SOBERANÍA ESTRATÉGICA (Dimensión Técnica)

   - Estado Empresario Argentino: conduce como nave insignia y tracción
     de compras públicas (compre nacional) sobre sectores estratégicos
     (energía, siderurgia, minería, logística multimodal, industria de
     defensa, electrónica nacional, alimentos y fármacos). La pyme
     privada se integra verticalmente detrás de esta cadena de valor.
   - Nacionalización del Comercio Exterior: defensa del valor de la
     producción criolla, marina mercante nacional, control de vías
     navegables, elevadores y puertos.
   - Nacionalización de Depósitos y Crédito: el ahorro nacional debe
     financiar la producción industrial, la colonización de tierras y la
     vivienda familiar, no la especulación ni la fuga.
   - Comunidad Capitalizada: el objetivo no es el estatismo total ni el
     colectivismo, sino la difusión universal de la propiedad privada y
     la dignificación del trabajo.
   - Soberanía Estratégica y Falacia Ambientalista: cuando analices
     vedas, reservas naturales o suspensiones de pesca/minería/energía
     bajo argumentos ecológicos, evaluá el impacto geopolítico real. Si
     la restricción frena a la producción y al trabajo nacional pero
     beneficia de facto la depredación extranjera en los límites
     fronterizos, denuncialo como "ecologismo colonial" o "entrega
     pasiva del recurso estratégico".

=======================================================================
III. TRADUCTOR DE EUFEMISMOS Y AUDITORÍA DE LETRA CHICA
=======================================================================

Tu análisis no es pasivo. Operás como auditor popular. Cuando el Boletín
Oficial intenta disfrazar medidas contra el pueblo, las traducís al
lenguaje de la realidad con estas equivalencias:

1. "Modernización / Simplificación del Estado" = reducción de controles
   públicos, despido de trabajadores estatales estratégicos o
   desmantelamiento de áreas de soberanía.
2. "Desregulación / Eficiencia de Mercados" = liberación de tarifas y
   precios para permitir la usura y el monopolio de corporaciones
   concentradas.
3. "Optimización Impositiva / Incentivo a la Inversión" = beneficios
   fiscales para el gran capital extranjero o evasión legalizada en
   detrimento de la recaudación nacional.
4. "Actualización de Regímenes Laborales" = precarización del
   trabajador, quita de convenios colectivos y desprotección frente al
   despido.
5. "Articulación Público-Privada" = privatización encubierta de recursos
   públicos o transferencia de la rentabilidad del Estado a manos
   privadas.

AUDITORÍA OBLIGATORIA DE LETRA CHICA:

- Buscá siempre los artículos finales ("De forma", prórrogas o anexos
  colgados). Las peores entregas se ocultan en derogaciones de leyes
  anteriores mencionadas al pasar en los considerandos.
- Si una norma ratifica un DNU, identificá qué ley del Congreso está
  siendo desplazada y mencionalo en el campo "criollo".
- Si la norma beneficia al capital concentrado financiero (por ejemplo
  resoluciones de CNV o ARCA), identificá quiénes se quedan con la renta
  del pueblo.

=======================================================================
IV. TONO Y ESTILO
=======================================================================

- Analítico, propositivo, firme contra la entrega colonial y el
  entreguismo burocrático, pero fraterno y constructivo hacia el pueblo
  y los patriotas de cualquier extracción.
- Lenguaje firme, directo, concreto y fundado en hechos.
- Sin rodeos academicistas, sin eufemismos técnicos, sin neutralidad
  falsa.
- Español de Argentina, tuteo, tono militante pero no panfletario.
- No inventes información que no aparezca en el texto original.
- Si la norma es ambigua, decilo expresamente.
- SINTÉTICO Y AL HUESO. El laburante lee esto en el celular, mientras
  viaja o mientras trabaja. Cada palabra tiene que aportar.

=======================================================================
V. FORMATO DE RESPUESTA (JSON ESTRICTO)
=======================================================================

Devolvé ÚNICAMENTE un objeto JSON válido, sin texto antes ni después,
sin backticks, sin markdown, sin explicaciones adicionales.

ESTRUCTURA EXACTA DEL JSON:

{
  "publicar": true | false,
  "jurisdiccion": "nacion" | "pba" | "caba",
  "titulo": "Tipo y número de norma, sin descripción",
  "criollo": "Explicación popular y sintética del impacto, con análisis doctrinario aplicado.",
  "afecta": "- <b>Título corto 1:</b> explicación breve\\n- <b>Título corto 2:</b> explicación breve",
  "letraChica": "Hallazgo más importante de la auditoría de letra chica."
}

REGLAS DE EXTENSIÓN (OBLIGATORIAS - SINTETIZAR):

- "criollo": MÁXIMO 350 caracteres. Sintético, directo, sin vueltas.
  Priorizá: qué cambia + a quién beneficia + a quién perjudica.
  NO repitas el título de la norma dentro del criollo.
  NO uses frases de relleno ("cabe destacar", "es importante señalar").
- "afecta": MÍNIMO 2, MÁXIMO 3 ítems. Cada ítem MÁXIMO 100 caracteres
  (sin contar el título corto en negrita). Al hueso.
- "letraChica": MÁXIMO 200 caracteres. Solo el hallazgo más importante.
  Si no hay nada relevante, poné "Sin datos relevantes en letra chica."

REGLAS OBLIGATORIAS DEL JSON:

- "publicar": true si la norma tiene impacto REAL y CONCRETO sobre el
  pueblo trabajador (bolsillo, trabajo, derechos, soberanía, servicios
  públicos, industria, agro, pesca, transporte, vivienda, salud,
  educación). false si es una norma meramente administrativa,
  protocolar, de designación, o sin impacto real en la vida del
  laburante.
- "jurisdiccion" SIEMPRE en minúscula: "nacion", "pba" o "caba".
- "titulo" SOLO el tipo y número. Ejemplo: "Decreto 512/2026".
- "criollo" es texto plano, SIN etiquetas HTML. Un solo párrafo.
- "afecta" SÍ lleva etiquetas HTML <b>...</b> para los títulos cortos.
  Cada ítem va en línea nueva, separado por "\\n".
- "letraChica" es texto plano, SIN etiquetas HTML. Un solo párrafo.
- NO uses asteriscos (**), ni guiones bajos (_), ni backticks.
- Asegurate de que el JSON sea válido: llaves, comillas y comas correctas.
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
# 5. FUNCIONES PARA CABA
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
# 6. FUNCIONES PARA PBA
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

        # Buscar el bloque del boletín de hoy. El patrón es:
        # BOLETÍN N° XXXXX - DD/MM/YYYY
        # ... (más adelante en el mismo bloque)
        # href="/secciones/XXXXX/ver"
        patron_fecha = re.escape(fecha_hoy)
        indice_fecha = html.find(f"- {fecha_hoy}")

        if indice_fecha == -1:
            print(f"❌ PBA: No se encontró el boletín del {fecha_hoy}.")
            return None

        # Buscar el link /secciones/XXXXX/ver más cercano DESPUÉS del título
        # Buscamos desde la posición de la fecha hasta 5000 caracteres después
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

            for i, pagina in enumerate(pdf.pages):
                contenido = pagina.extract_text()
                if contenido:
                    texto.append(contenido)

        texto_completo = "\n".join(texto)
        print(f"✅ PBA: Texto extraído ({len(texto_completo)} caracteres).")

        # Patrón: DECRETO N° 1667/2026 | RESOLUCIÓN N° 256-XX-2026 | DISPOSICIÓN N° 1249-XX-2026
        patron_norma = r'((?:DECRETO|RESOLUCIÓN|DISPOSICIÓN)\s+N°\s+[\d\-A-Za-z/]+)'

        # Encontrar todas las posiciones de inicio de norma
        matches = list(re.finditer(patron_norma, texto_completo, re.IGNORECASE))

        normas = []
        for i, match in enumerate(matches):
            inicio = match.start()
            fin = matches[i + 1].start() if i + 1 < len(matches) else len(texto_completo)

            # Extraer título y texto
            titulo = match.group(1).strip()
            texto_norma = texto_completo[inicio:fin].strip()

            # Limpiar y limitar tamaño (evita tokens gigantes)
            texto_norma_limpio = " ".join(texto_norma.split())
            texto_norma_limpio = texto_norma_limpio[:3000]  # tope de seguridad

            # Si es muy corto, probablemente es un falso positivo
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
# 7. FILTRAR NORMAS RELEVANTES (compartida)
# =======================================================================

def filtrar_normas_relevantes(normas):
    """Aplica el filtro por palabras clave."""

    print(f"🎯 IPD: Filtrando {len(normas)} normas...")

    candidatas = []

    for norma in normas:
        sumario = norma.get("sumario", "").lower().strip()
        norma_str = norma.get("norma", "").lower()
        texto = f"{sumario} {norma_str}"

        # Excluir si el sumario arranca con palabra de designación
        if any(sumario.startswith(p) for p in INICIOS_EXCLUIR):
            continue

        # Excluir boletín oficial
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
# 8. CONSULTAR GROQ
# =======================================================================

def consultar_groq(norma, jurisdiccion):
    """Analiza una norma con Groq. Devuelve un dict o None."""

    titulo = norma.get("norma", "Sin título")
    print(f"🤖 Groq: Analizando '{titulo}'...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_key}"
    }

    norma_texto = (
        f"## NORMA A ANALIZAR\n\n"
        f"Jurisdicción: {jurisdiccion.upper()}.\n\n"
        f"Norma: {norma.get('norma', '')}.\n\n"
        f"Sumario oficial:\n{norma.get('sumario', '')}\n\n"
        f"Página del boletín: {norma.get('pagina', '')}"
    )

    payload_groq = {
        "model": modelo_groq,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": norma_texto}
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"}
    }

    try:
        res_groq = requests.post(url_groq, headers=headers, json=payload_groq, timeout=90)
        print(f"📡 Groq: Código {res_groq.status_code}")

        if res_groq.status_code != 200:
            print("❌ Groq rechazó la solicitud.")
            print(res_groq.text[:500])
            return None

        data = res_groq.json()

        try:
            contenido = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            print("❌ Estructura inesperada en Groq.")
            return None

        try:
            dictamen = json.loads(contenido)
            print("⚖️ Dictamen parseado.")
            return dictamen
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido: {e}")
            print(contenido[:500])
            return None

    except Exception as e:
        print(f"💥 Error con Groq: {e}")
        return None


# =======================================================================
# 9. VALIDAR DICTAMEN
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
# 10. ESCAPAR HTML
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
# 11. FORMATEAR PARA TELEGRAM
# =======================================================================

def formatear_para_telegram(dictamen):

    jurisdiccion = str(dictamen.get("jurisdiccion", "")).upper()
    titulo = escapar_html(dictamen.get("titulo", ""))
    criollo = escapar_html(dictamen.get("criollo", ""))
    afecta = escapar_html(dictamen.get("afecta", ""))

    mensaje = (
        "<b>📢 IPD: Alerta Temprana del Bolsillo Popular</b>\n\n"
        f"<b>📌 {jurisdiccion} | {titulo}</b>\n\n"
        f"<b>🔍 LA POSTA:</b>\n\n{criollo}\n\n"
        f"<b>⚠️ CÓMO TE AFECTA:</b>\n\n{afecta}\n\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "🌐 Sumate a la comunidad:\n"
        '<a href="https://ipdboletin.github.io">ipdboletin.github.io</a>'
    )

    return mensaje


# =======================================================================
# 12. ENVIAR A TELEGRAM
# =======================================================================

def enviar_telegram(mensaje):

    payload_tg = {
        "chat_id": chat_id_tg,
        "text": mensaje,
        "parse_mode": "HTML"
    }

    # Intentar 2 veces (con timeout de 60s)
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
# 13. GUARDAR EN datos.js
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
        f'    afecta: "{limpiar(dictamen["afecta"])}",\n'
        f'    letraChica: "{limpiar(dictamen["letraChica"])}"\n'
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
# 14. PROCESAR UNA JURISDICCIÓN
# =======================================================================

def procesar_jurisdiccion(jurisdiccion):
    """Procesa CABA o PBA. Devuelve lista de resultados."""

    print(f"\n{'═' * 70}")
    print(f"🗺️ PROCESANDO {jurisdiccion.upper()}")
    print(f"{'═' * 70}\n")

    # PASO 1 — Bajar PDF
    if jurisdiccion == "caba":
        ruta_pdf = bajar_pdf_boletin_caba()
        normas = extraer_normas_caba(ruta_pdf) if ruta_pdf else []
    elif jurisdiccion == "pba":
        id_boletin = obtener_id_boletin_pba()
        ruta_pdf = bajar_pdf_boletin_pba(id_boletin) if id_boletin else None
        normas = extraer_normas_pba(ruta_pdf) if ruta_pdf else []
    else:
        print(f"❌ Jurisdicción desconocida: {jurisdiccion}")
        return []

    if not normas:
        print(f"⚠️ No se encontraron normas en {jurisdiccion.upper()}.")
        return []

    # PASO 2 — Filtrar
    candidatas = filtrar_normas_relevantes(normas)

    if not candidatas:
        print(f"⚠️ Ninguna norma de {jurisdiccion.upper()} pasó el filtro.")
        return []

    # PASO 3 — Analizar cada una
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

        if not validar_dictamen(dictamen):
            print(f"⚠️ Dictamen inválido. Se saltea.")
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
# 15. PROCESO PRINCIPAL
# =======================================================================

def ejecutar_patrullaje():

    print("")
    print("=" * 70)
    print("🛡️ IPD - INFORMACIÓN PARA LA DEFENSA")
    print("🕵️ Iniciando patrullaje...")
    print("=" * 70)

    todos = {}

    # CABA
    todos["caba"] = procesar_jurisdiccion("caba")

    # PBA
    todos["pba"] = procesar_jurisdiccion("pba")

    # RESUMEN FINAL
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
# 16. EJECUTAR
# =======================================================================

if __name__ == "__main__":
    ejecutar_patrullaje()
