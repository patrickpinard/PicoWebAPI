# Web PWA APP de contrôle du module 8 relais WaveShare/Pico-W via via API's 

## Vue d'ensemble de la solution

Ce système permet de contrôler jusqu'à 8 relais du module waveshare via un Raspberry Pi Pico W. 

Il offre une interface REST API et intègre des fonctionnalités de surveillance système, de journalisation des événements et de persistance des états.

## Architecture du Système

Le système est composé de deux parties principales :
- Un serveur Flask (`app.py`) qui sert l'interface web et fait le pont avec le Pico
- Un client Pico (`main.py`) qui gère les relais et expose une API REST
Référence du module: https://www.waveshare.com/pico-relay-b.htm

![](/images/pico-relay-b-1.jpg)

![](/images/pico-relay-b-2.jpg)

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

### Caractéristiques Principales

- Contrôle de 8 relais individuels
- Interface web responsive
- Monitoring système en temps réel
- Journalisation des événements
- Persistance des états des relais
- Support SSL/TLS optionnel
- Mode PWA (Progressive Web App)

## Serveur Web Flask (app.py)

### Configuration

Le serveur Flask est configuré pour :
- Écouter sur toutes les interfaces (`0.0.0.0`)
- Port 80 par défaut
- CORS activé pour `http://localhost`
- Communication avec le Pico sur `http://192.168.1.109`

### Points d'Accès (Routes)

#### Routes Principales

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET, POST | Page d'accueil avec état des relais |
| `/relais` | GET, POST | Interface de contrôle des relais |
| `/system` | GET, POST | Informations système |
| `/parameters` | GET, POST | Page de paramètres |
| `/events` | GET, POST | Journal des événements |

#### Routes PWA

| Route | Méthode | Description |
|-------|---------|-------------|
| `/__service-worker.js` | GET | Service Worker pour PWA |
| `/__manifest.json` | GET | Manifeste PWA |

#### Routes API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/get_relay_state` | GET, POST | Obtenir l'état des relais |
| `/reboot` | GET, POST | Redémarrer le Pico |

### Gestion des Erreurs

Le serveur implémente une gestion robuste des erreurs avec :
- Timeout de 3 secondes pour les requêtes
- États par défaut en cas de déconnexion
- Gestion des exceptions de connexion

## Client Pico (main.py)

### Classe Config

Configuration centralisée du système :

```python
RELAY_PINS = {
    "1": 21, "2": 20, "3": 19, "4": 18,
    "5": 17, "6": 16, "7": 15, "8": 14
}
```

Autres configurations :
- PIN LED RGB : 13
- PIN Buzzer : 6
- Fichier d'états : "relay_states.json"
- Limite événements : 50

### Classe RelaySystem

#### Fonctionnalités Principales

1. **Gestion des Relais**
   - Initialisation des pins
   - Contrôle individuel
   - Contrôle groupé
   - Persistance des états

2. **Monitoring Système**
   - Température CPU
   - Tension système
   - Utilisation mémoire
   - État réseau
   - Horodatage

3. **Journalisation**
   - Buffer circulaire (50 événements)
   - Horodatage des événements
   - Catégorisation (INFO, WARNING, ERROR)

#### Points d'Accès API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/relays` | GET | État de tous les relais |
| `/relay/<id>/<state>` | GET, POST | Contrôle d'un relais |
| `/allrelays/<state>` | GET, POST | Contrôle de tous les relais |
| `/system` | GET | Informations système |
| `/reboot` | GET, POST | Redémarrage système |
| `/events` | GET, POST | Journal des événements |

### Sécurité

Le système supporte :
- Connexion WiFi sécurisée
- SSL/TLS optionnel (port 443)
- Fallback sur port 80 si SSL non disponible

## Installation

### Prérequis

1. Raspberry Pi Pico W
2. Serveur Python avec Flask
3. Module de 8 relais
4. Connexion réseau

### Configuration Requise

Fichier `secrets.py` contenant :
```python
ssid = "votre_ssid"
pwd = "votre_mot_de_passe"
ssl_key = "chemin_vers_clé_ssl"  # Optionnel
ssl_cert = "chemin_vers_cert_ssl"  # Optionnel
location = "emplacement_dispositif"
contact = "contact_administrateur"
```

## Utilisation

### Démarrage du Serveur

```bash
sudo python3 app.py
```

### Accès à l'Interface

1. Naviguer vers `http://<adresse_ip_serveur>`
2. L'interface affiche :
   - État des relais
   - Informations système
   - Journal des événements
   - Options de configuration

## Surveillance et Maintenance

### Indicateurs LED

- LED RGB pour l'état système
- LED embarquée pour diagnostic

### Journalisation

Le système maintient un journal des 50 derniers événements avec :
- Horodatage
- Type d'événement
- Message détaillé

### Diagnostic

1. Vérification de connexion : `http://<adresse_ip_pico>/system`
2. État des relais : `http://<adresse_ip_pico>/relays`
3. Journal système : `http://<adresse_ip_pico>/events`

## Développement Futur

Axes d'amélioration potentiels :
1. Authentification utilisateur
2. Planification des tâches
3. Intégration MQTT
4. Interface API étendue
5. Support de configurations avancées


