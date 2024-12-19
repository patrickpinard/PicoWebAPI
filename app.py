# Version 1 - Flask web PWA to maange Raspberry Pico Relay Board with API's
# Patrick Pinard - 2024


from flask import Flask, render_template, jsonify
import requests
import os, time
from flask_cors import CORS
import json
#from myLOGLib import LogEvent, events

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost"}})
app.secret_key = os.urandom(12)

URL_PICO = "http://192.168.1.109"

default_relays=[{"5": False, "4": False, "7": False, "6": False, "1": False, "8": False, "3": False, "2": False}]

default_system = {'ip_address': "unknown",
            'ssid': "unknown",
            'free_memory': "unknown",
            'memory': "unknown",
            'allocated_memory' : "unknown",
            'temperature': "unknown",
            'voltage': "unknown", 
            'time': "unknown",
            'date': "unknown",
            'location': "unknown",
            'contact': "unknown"}

###### PWA files  ########


@app.route("/__service-worker.js", methods=["GET"])
def serviceworker():

    return app.send_static_file("__service-worker.js")


@app.route("/__manifest.json", methods=["GET"])
def manifest():

    return app.send_static_file("__manifest.json")

def is_connected():

    url = URL_PICO + "/is_connected"
    
    try:
        response = requests.get(url,timeout=3)
        return True 
    except :
        return False


def get_relay_state():
    """
    Retourne la page html info.html
    """
    url = URL_PICO + "/relays"
    try:
        response = requests.get(url,timeout=3)
        relays = response.json()
        print(relays)
        return (relays)
    except requests.exceptions.ConnectionError:
        return (" ...no relay states")
    
###### routes  ########



@app.route("/", methods=["GET","POST"])
def home():
    """
    Retourne la page html principale 
    """
    if is_connected():
        relays = get_relay_state()
        return render_template("relais.html", relays=relays, connected=True)
    else:
        relays=default_relays
        return render_template("relais.html", relays=relays, connected=False)


@app.route("/relais", methods=["GET","POST"])
def relais():
    """
    Retourne la page relais.html
    """
    url = URL_PICO + "/relays"
    try:
        response = requests.get(url,timeout=3)
        relays = response.json()
        return render_template("relais.html", relays=relays, connected=True)
    except: 
        relays=default_relays
        return render_template("relais.html", relays=relays, connected=False)

@app.route("/system", methods=["GET","POST"])
def system():
    """
    Retourne la page system.html
    """
    url = URL_PICO + "/system"
    try:
        response = requests.get(url,timeout=3)
        system = response.json()
        return render_template("system.html", system=system, connected=True)
    except :
        return render_template("system.html", system=default_system,connected=False)
    
@app.route("/parameters", methods=["GET","POST"])
def parameters():
    """
    Retourne la page html parameters.html
    """

    return render_template("parameters.html", connected=True)


@app.route("/events", methods=["GET","POST"])
def events():
    """
    Retourne la page html events.html
    """
    
    url = URL_PICO + "/events"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        events_data = response.json()
        return render_template("events.html", events=events_data, connected=True)
    except: 
        return render_template("events.html", events=[], connected=False)
    
@app.route("/get_relay_state", methods=["GET","POST"])
def get_relay_state():
    """
    Retourne la page html info.html
    """
    url = URL_PICO + "/relays"
    try:
        response = requests.get(url,timeout=3)
        relays = response.json()
        return jsonify(relays)
    except requests.exceptions.ConnectionError:
        return (" ...no relay states") 
    

@app.route("/reboot", methods=["GET","POST"])
def reboot():
    """
    Reboot Pico
    """
    url = URL_PICO + "/reset"
    try:
        response = requests.get(url,timeout=3)
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.ConnectionError:
        print("Erreur : Impossible de se connecter au Pico.")
    except requests.exceptions.Timeout:
        print("Erreur : La requête a expiré.")
    except requests.exceptions.RequestException as e:
        print(f"Erreur générale : {e}")
    return (" ...no reboot")


if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80, debug=False)