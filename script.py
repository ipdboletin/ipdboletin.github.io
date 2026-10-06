import os
import requests
from pathlib import Path

# 1. LEER LAS CREDENCIALES DEL ARCHIVO .ENV
ruta_actual = Path(__file__).resolve().parent
ruta_env = ruta_actual / ".env"

token = None
chat_id = None

if ruta_env.exists():
    with open(ruta_env, "r", encoding="utf-8") as f:
        for linea in f:
            linea_limpia = linea.strip()
            if linea_limpia and not linea_limpia.startswith("#"):
                clave, valor = linea_limpia.split("=", 1)
                if clave.strip() == "TELEGRAM_TOKEN":
                    token = valor.strip()
                elif clave.strip() == "TELEGRAM_CHAT_ID":
                    chat_id = valor.strip()
else:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

# 2. FUNCIÓN DE DESPACHO CON URL SEGURA CONTRA ERRORES
def enviar_alerta_telegram(mensaje, bot_token, destino_id):
    if not bot_token or not destino_id:
        print("❌ Error: No se encontraron los tokens.")
        return
    
    # Construcción por componentes aislados para asegurar la sintaxis exacta de la API
    dominio_api = "https://api.telegram.org"
    prefijo_bot = "/bot"
    metodo_envio = "/sendMessage"
    
    # Se ensambla la URL combinando cada pieza de forma estricta
    url = dominio_api + prefijo_bot + str(bot_token).strip() + metodo_envio
    
    payload = {
        "chat_id": str(destino_id).strip(),
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    print(f"Ejecutando POST a la URL ensamblada: {url}")
    try:
        respuesta = requests.post(url, json=payload, timeout=15)
        resultado = respuesta.json()
        
        if respuesta.status_code == 200 and resultado.get("ok"):
            print("🚀 ¡ALERTA DESPACHADA CON ÉXITO EN EL CANAL!")
        else:
            print(f"❌ Error de la API: {resultado.get('description')}")
    except Exception as e:
        print(f"💥 Falló la conexión de red: {e}")

if __name__ == "__main__":
    enviar_alerta_telegram("🔔 Test de ruteo definitivo y corregido exitoso.", token, chat_id)
