#!/usr/bin/env python3

import json
import time
import socket
import meshtastic.tcp_interface

# CONFIGURAZIONE
# MeshCom
MESHCOM_UDP_IP = "0.0.0.0"
MESHCOM_UDP_PORT = 1799
# Nodo MeshCom che fa da bridge: solo i frame destinati a questo nodo verranno inoltrati
MESHCOM_BRIDGE_NODE = "IK5XMK-99"
# Meshtastic
MESHTASTIC_HOST = "192.168.1.155"
MESHTASTIC_PORT = 4403
# Canale di default Meshtastic per i broadcast (Primary = 0)
MESHTASTIC_CHANNEL = 1

# PROCEDURE E FUNZIONI

def open_udp():
    """Apre la socket UDP in ascolto per MeshCom"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((MESHCOM_UDP_IP, MESHCOM_UDP_PORT))
    print(f"[INFO] Socket UDP in ascolto su {MESHCOM_UDP_IP}:{MESHCOM_UDP_PORT}")
    return sock

def read_from_meshcom(sock):
    """Legge da UDP MeshCom e restituisce i frame validi (src, dst, msg)"""
    try:
        data, addr = sock.recvfrom(4096)
        if not data:
            return None

        text = data.decode(errors="ignore").strip()
        if "{" not in text or "}" not in text:
            return None

        js = text[text.find("{"):text.rfind("}") + 1]
        payload = json.loads(js)

        # Verifica campi
        if not all(k in payload for k in ("src", "dst", "msg")):
            print("[SCARTO] Frame privo di campi richiesti:", text)
            return None

        src = payload["src"]
        dst = payload["dst"]
        msg = payload["msg"]

        # Rimuove eventuale parte ACK dopo '{'
        if "{" in msg:
            msg = msg.split("{")[0]
            msg = msg.strip()

        print(f"[RX] Frame ricevuto da MeshCom UDP {addr}: src={src}, dst={dst}, msg={msg}")
        return src, dst, msg

    except json.JSONDecodeError:
        print("[ERRORE] JSON non valido:", data)
        return None
    except Exception as e:
        print(f"[ERRORE] {e}")
        return None

def send_to_meshtastic(message: str, dest: str | None):
    """Invia un messaggio a Meshtastic via TCP"""
    try:
        print(f"[INFO] Connessione TCP a Meshtastic {MESHTASTIC_HOST}:{MESHTASTIC_PORT}...")
        iface = meshtastic.tcp_interface.TCPInterface(MESHTASTIC_HOST, MESHTASTIC_PORT)
        time.sleep(1)  # breve pausa per stabilizzare la connessione

        if dest:
            print(f"[TX] Invio a nodo {dest}: {message}")
            iface.sendText(text=message, destinationId=dest)
        else:
            print(f"[TX] Invio broadcast sul canale {MESHTASTIC_CHANNEL}: {message}")
            iface.sendText(text=message, channelIndex=MESHTASTIC_CHANNEL)

        iface.close()
        print("[INFO] Messaggio inviato e connessione chiusa.\n")

    except Exception as e:
        print(f"[ERRORE] Invio a Meshtastic fallito: {e}")


# MAIN LOOP

if __name__ == "__main__":
    print("[START] Avvio bridge MeshCom -> Meshtastic")

    sock = open_udp()

    # Ciclo infinito
    while True:
        frame = read_from_meshcom(sock)
        if frame is None:
            continue

        src, dst, msg = frame

        # Accetta solo se destinato al nodo bridge
        if dst != MESHCOM_BRIDGE_NODE:
            print(f"[SCARTO] Frame destinato a {dst}, non a {MESHCOM_BRIDGE_NODE}")
            continue

        msg = msg.strip()
        # msg = src + ' ' + msg + ' -via mc2meshtastic gw' # mod by IZ0MJE
        
        # Se inizia con "!" è un messaggio verso un nodo specifico
        if msg.startswith("!"):
            parts = msg.split(" ", 1)
            dest = parts[0]
            text = parts[1] if len(parts) > 1 else "(vuoto)"
            send_to_meshtastic(text, dest)
        else:
            # Broadcast

            send_to_meshtastic(msg, None)
