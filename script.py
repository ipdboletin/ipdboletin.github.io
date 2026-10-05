import os
import requests

# 1. Recuperar los secretos
token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

# 2. Alerta Oficial de IPD
titulo = '📢 IPD: Alerta Temprana del Bolsillo Popular'
cuerpo = (
    "🔍 EN CRIOLLO: El motor autónomo de la trinchera está oficialmente en marcha.\n"
    "⚠️ CÓMO TE AFECTA: Monitoreo activado al 100% en internet. Vos descansás y la máquina labura por la patria.\n"
    "📝 LA LETRA CHICA: Código limpio ejecutado desde servidores libres de candados corporativos."
)

mensaje_final = f"{titulo}\n\n{cuerpo}\n\n━━━━━━━━━━━━━━━━━━━\n🌐 Sumate a la comunidad y registrá tu mail:\nhttps://github.io"

# 3. Envío directo
url = f"https://telegram.org{token}/sendMessage"
payload = {"chat_id": chat_id, "text": mensaje_final}

res = requests.post(url, json=payload)

# Imprime el resultado real para auditar en pantalla
print(f"Respuesta del servidor de Telegram: {res.status_code}")
print(f"Detalle del error: {res.text}")

if res.status_code == 200:
    print("¡Alerta despachada con éxito!")
else:
    raise Exception(f"Error en el despacho: {res.text}")
