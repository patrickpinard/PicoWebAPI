# Configuration WiFi
ssid = "yourWifiSSID"
pwd = "yourWifiPASSWORD"

# Configuration SSL
# Méthode alternative pour charger les certificats
try:
    with open('ssl_key.pem', 'r') as f:
        ssl_key = f.read()
    with open('ssl_cert.pem', 'r') as f:
        ssl_cert = f.read()
except:
    # Configuration par défaut si les fichiers n'existent pas
    ssl_key = None
    ssl_cert = None

