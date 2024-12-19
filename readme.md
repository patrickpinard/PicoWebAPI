# Documentation du système de contrôle de relais Pico W

https://www.waveshare.com/pico-relay-b.htm

![](/images/pico-relay-b-1.png)

![](/images/pico-relay-b-2.png)


## Table des matières
- [Vue d'ensemble](#vue-densemble)
- [Configuration](#configuration)
- [Composants matériels](#composants-matériels)
- [API REST](#api-rest)
- [Classes principales](#classes-principales)
- [Fonctionnalités](#fonctionnalités)
- [Gestion des états](#gestion-des-états)
- [Surveillance système](#surveillance-système)

## Vue d'ensemble

Ce système permet de contrôler jusqu'à 8 relais via un Raspberry Pi Pico W. Il offre une interface REST API et intègre des fonctionnalités de surveillance système, de journalisation des événements et de persistance des états.

### Caractéristiques principales
- Contrôle de 8 relais indépendants
- Interface REST API
- Indicateur LED RGB
- Surveillance système (température, mémoire, tension)
- Journalisation des événements
- Sauvegarde persistante des états
- Support SSL optionnel

## Configuration

### Configuration matérielle
```python
RELAY_PINS = {
    "1": 21, "2": 20, "3": 19, "4": 18,
    "5": 17, "6": 16, "7": 15, "8": 14
}
LED_PIN = 13
BUZZER_PIN = 6
```

### Fichiers requis
- `secrets.py` : Contient les informations de connexion WiFi et SSL
- `relay_states.json` : Stockage persistant des états des relais
- `mm_wlan.py` : Module de gestion WiFi

## Composants matériels
- Raspberry Pi Pico W
- 8 relais
- LED RGB (NeoPixel)
- Buzzer
- LED embarquée

## API REST

### Endpoints disponibles

#### État des relais
```http
GET /relays
```
Retourne l'état de tous les relais
```json
{
    "1": false,
    "2": true,
    ...
    "8": false
}
```

#### Contrôle d'un relai
```http
POST /relay/<id>/<state>
```
- `id` : Identifiant du relai (1-8)
- `state` : État souhaité (0/1)

#### Contrôle de tous les relais
```http
POST /allrelays/<state>
```
- `state` : État souhaité (0/1)

#### Informations système
```http
GET /system
```
Retourne les informations système :
```json
{
    "ip_address": "192.168.1.100",
    "ssid": "MyNetwork",
    "free_memory": "100",
    "temperature": "25.5",
    "voltage": "3.3",
    "time": "12:34:56",
    "date": "31.12.2024"
}
```

#### Journal des événements
```http
GET /events
```
Retourne les derniers événements système

#### Redémarrage
```http
POST /reboot
```
Redémarre le système

## Classes principales

### Class Config
Gère la configuration centralisée :
- Mapping des pins
- Définitions des couleurs
- Configuration système

### Class RelaySystem
Gère l'ensemble du système :
- Initialisation des relais
- Gestion des états
- Journalisation
- Surveillance système

## Fonctionnalités

### Gestion des relais
- Contrôle individuel des relais
- Contrôle groupé
- Sauvegarde automatique des états
- Restauration des états au démarrage

### Surveillance système
- Température du processeur
- Tension d'alimentation
- Utilisation mémoire
- État de la connexion WiFi
- Horodatage

### Journalisation
- Conservation des 200 derniers événements
- Horodatage des événements
- Types d'événements : INFO, WARNING, ERROR

## Gestion des états

### Persistance
Les états des relais sont sauvegardés dans `relay_states.json` :
```json
{
    "1": false,
    "2": true,
    ...
    "8": false
}
```

### Restauration
Au démarrage, le système :
1. Charge les états sauvegardés
2. Configure les relais selon ces états
3. Initialise le système de journalisation

## Surveillance système

### Mesures disponibles
- Température CPU
- Tension d'alimentation
- Mémoire libre/utilisée
- État de la connexion réseau

### Format des événements
```json
{
    "message": "INFO: Relay 1 set to True",
    "time": "12:34:56",
    "date": "31/12/2024"
}
```

## Sécurité
- Support SSL optionnel
- Authentification WiFi
- Stockage sécurisé des credentials dans `secrets.py`

## Dépannage

### Problèmes courants
1. **Perte de connexion WiFi**
   - Vérifier les credentials dans `secrets.py`
   - Vérifier la portée du signal

2. **États des relais incorrects**
   - Vérifier `relay_states.json`
   - Redémarrer le système

3. **Erreurs mémoire**
   - Surveillance de l'utilisation mémoire via `/system`
   - Nettoyage automatique du journal des événements

# Documentation de l'interface Web Flask pour le système de relais

## Table des matières
- [Vue d'ensemble](#vue-densemble)
- [Configuration](#configuration)
- [Routes et Endpoints](#routes-et-endpoints)
- [Progressive Web App](#progressive-web-app)
- [Gestion des erreurs](#gestion-des-erreurs)
- [Installation](#installation)
- [Développement](#développement)

## Vue d'ensemble

Cette application Flask sert d'interface web pour un système de contrôle de relais Pico W. Elle fournit une interface utilisateur web complète et gère la communication avec le Pico W via une API REST.


![](/images/relais.png)
![](/images/system2.png)
![](/images/events.png)

### Caractéristiques principales
- Interface web responsive
- Support PWA (Progressive Web App)
- Gestion des états de connexion
- Visualisation des événements système
- Interface de contrôle des relais
- Monitoring système

## Configuration

### Configuration de base
```python
URL_PICO = "http://192.168.1.109"
app.secret_key = os.urandom(12)
```

### CORS
```python
CORS(app, resources={r"/*": {"origins": "http://localhost"}})
```

### États par défaut
```python
default_relays = [{"5": False, "4": False, "7": False, "6": False,
                   "1": False, "8": False, "3": False, "2": False}]

default_system = {
    'ip_address': "unknown",
    'ssid': "unknown",
    'free_memory': "unknown",
    'temperature': "unknown",
    'voltage': "unknown",
    'time': "unknown",
    'date': "unknown",
    'location': "unknown",
    'contact': "unknown"
}
```

## Routes et Endpoints

### Pages principales

#### Page d'accueil
```http
GET /
```
Affiche la page principale avec l'état des relais

#### Page des relais
```http
GET /relais
```
Affiche l'interface de contrôle des relais

#### Page système
```http
GET /system
```
Affiche les informations système

#### Page des événements
```http
GET /events
```
Affiche le journal des événements

#### Page des paramètres
```http
GET /parameters
```
Affiche la page de configuration

### API Endpoints

#### État des relais
```http
GET /get_relay_state
```
Retourne l'état actuel des relais en JSON

#### Redémarrage
```http
GET /reboot
```
Déclenche un redémarrage du Pico W

## Progressive Web App

### Fichiers PWA
- `/__service-worker.js` : Service worker pour le fonctionnement hors ligne
- `/__manifest.json` : Manifeste de l'application

### Routes PWA
```python
@app.route("/__service-worker.js")
@app.route("/__manifest.json")
```

## Gestion des erreurs

### Vérification de connexion
```python
def is_connected():
    try:
        response = requests.get(url, timeout=3)
        return True
    except:
        return False
```

### Gestion des timeouts
- Timeout de 3 secondes pour toutes les requêtes
- Retour aux valeurs par défaut en cas d'erreur
- Affichage des états de déconnexion dans l'interface

## Installation

### Prérequis
```bash
pip install flask flask-cors requests
```

### Structure des fichiers
```
/
├── app.py
├── static/
│   ├── __service-worker.js
│   └── __manifest.json
└── templates/
    ├── relais.html
    ├── system.html
    ├── events.html
    └── parameters.html
```

## Développement

### Lancement du serveur
```bash
python app.py
```

### Configuration de développement
```python
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80, debug=False)
```

### Bonnes pratiques
1. Tous les appels API ont un timeout de 3 secondes
2. Les états par défaut sont utilisés en cas d'erreur
3. L'état de connexion est vérifié pour chaque template
4. Les erreurs sont gérées silencieusement pour l'utilisateur

## Notes de sécurité
- La clé secrète est générée aléatoirement au démarrage
- CORS est configuré pour localhost uniquement
- Les timeouts évitent les blocages

## Dépannage

### Problèmes courants

1. **Erreur de connexion au Pico**
   - Vérifier l'URL dans `URL_PICO`
   - Vérifier que le Pico est en ligne
   - Vérifier le réseau local

2. **Page blanche**
   - Vérifier les logs Flask
   - Vérifier les templates
   - Vérifier la connexion au Pico

3. **États incorrects**
   - Rafraîchir la page
   - Vérifier la connexion
   - Redémarrer le Pico
