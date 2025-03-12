#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diese Anwendung führt eine Agenten-Konversation durch und verarbeitet dabei sowohl Text- als auch Bild- (bzw. PDF-) Dateien.
Die folgenden Funktionen beinhalten unter anderem:
    - Benutzer- und Diskussionsverwaltung mittels JSON und SQLite
    - Kommunikation mit der Gemini API (unter Verwendung von Retry-Mechanismen)
    - Fehlerbehandlung und Logging
Für weitere Details siehe Kommentare in den einzelnen Funktionen.
"""

import re
import logging
import datetime
import json
import hashlib
import os
import time
import random
from collections import defaultdict
from typing import List, Dict, Tuple, Any, Union
import sqlite3
from jsonschema import validate, ValidationError
from docx import Document
from docx.shared import Inches
import streamlit as st
import google.generativeai as genai
from google.generativeai.types.generation_types import StopCandidateException
import tornado
import mimetypes

# Konstanten für Modelle und API-Parameter
MODEL_NAME_TEXT = "gemini-2.0-pro-exp-02-05"  # Alternativ: "gemini-1.5-pro-latest"
MODEL_NAME_VISION = "gemini-2.0-flash"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_SLEEP_SECONDS = 60
API_MAX_RETRIES = 3
SUMMARY_SLEEP_SECONDS = 10

AUDIT_LOG_FILE = "audit_log.txt"  # Wird aktuell nicht verwendet
EXPIRATION_TIME_SECONDS = 300  # Wird aktuell nicht verwendet
ROLE_PERMISSIONS = {
    "user": ["REQ", "DATA"],
    "admin": ["REQ", "DATA", "CALC", "IF", "AI"]
}
PRIORITY_MAP = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}  # Wird aktuell nicht verwendet

USER_DATA_FILE = "user_data.json"
DISCUSSION_DB_FILE = "discussion_data.db"
RATING_DATA_FILE = "rating_data.json"
AGENT_CONFIG_FILE = "agent_config.json"

# JSON-Schemas für die Validierung
USER_DATA_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
            "type": "object",
            "properties": {"password": {"type": "string"}},
            "required": ["password"]
        }
    }
}

AGENT_CONFIG_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "personality": {"type": "string", "enum": ["kritisch", "visionär", "konservativ", "neutral"]},
            "description": {"type": "string"}
        },
        "required": ["name", "personality", "description"]
    }
}

# Hilfsfunktionen für JSON (Laden/Speichern/Validieren)
def load_json_data(filename: str, schema: dict = None) -> Dict[str, Any]:
    """
    Lädt JSON-Daten aus einer Datei und validiert diese (falls ein Schema angegeben ist).
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if schema:
                validate(instance=data, schema=schema)
            return data
    except FileNotFoundError:
        logging.warning(f"Datei '{filename}' nicht gefunden. Starte mit leeren Daten.")
        return {}
    except (json.JSONDecodeError, ValidationError) as e:
        logging.error(f"Fehler beim Lesen von '{filename}': {e}")
        return {}

def save_json_data(data: Dict[str, Any], filename: str) -> None:
    """
    Speichert JSON-Daten in eine Datei.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.error(f"Fehler beim Schreiben in Datei '{filename}': {e}")

# Funktionen zur Benutzerverwaltung
def load_user_data() -> Dict[str, Any]:
    return load_json_data(USER_DATA_FILE, USER_DATA_SCHEMA)

def save_user_data(user_data: Dict[str, Any]) -> None:
    save_json_data(user_data, USER_DATA_FILE)

def load_rating_data() -> Dict[str, Any]:
    return load_json_data(RATING_DATA_FILE)

def save_rating_data(rating_data: Dict[str, Any]) -> None:
    save_json_data(rating_data, RATING_DATA_FILE)

def load_agent_config() -> List[Dict[str, str]]:
    return load_json_data(AGENT_CONFIG_FILE, AGENT_CONFIG_SCHEMA)

def hash_password(password: str) -> str:
    """
    Erzeugt einen SHA-256 Hash aus dem übergebenen Passwort.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """
    Überprüft, ob das Passwort mit dem gehashten Passwort übereinstimmt.
    """
    return hash_password(password) == hashed

def register_user(username: str, password: str) -> str:
    """
    Registriert einen neuen Benutzer, wenn der Nutzername und das Passwort gültig sind.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return "Ungültiger Nutzername."
    if len(password) < 8:
        return "Passwort muss mindestens 8 Zeichen lang sein."
    user_data = load_user_data()
    if username in user_data:
        return "Nutzername bereits vergeben."
    user_data[username] = {"password": hash_password(password)}
    save_user_data(user_data)
    return "Registrierung erfolgreich."

def login_user(username: str, password: str) -> Tuple[str, Union[str, None]]:
    """
    Loggt einen Benutzer ein, falls die Anmeldedaten stimmen.
    """
    user_data = load_user_data()
    if username in user_data and verify_password(password, user_data[username]["password"]):
        return "Login erfolgreich.", username
    return "Login fehlgeschlagen.", None

# Funktionen zur Datenbankverwaltung (SQLite)
def create_discussion_table():
    """
    Erstellt die Tabelle für Diskussionen in der SQLite-Datenbank, falls sie nicht existiert.
    """
    conn = sqlite3.connect(DISCUSSION_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discussions (
            discussion_id TEXT PRIMARY KEY,
            topic TEXT,
            agents TEXT,
            chat_history TEXT,
            summary TEXT,
            user TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

create_discussion_table()  # Tabelle beim Start sicherstellen

def save_discussion_data_db(discussion_id: str, topic: str, agents: List[str],
                              chat_history: List[Dict], summary: str, user: str = None) -> None:
    """
    Speichert die Diskussionsdaten in der SQLite-Datenbank.
    """
    conn = sqlite3.connect(DISCUSSION_DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO discussions (discussion_id, topic, agents, chat_history, summary, user)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (discussion_id, topic, json.dumps(agents), json.dumps(chat_history), summary, user))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Speichern der Diskussion '{discussion_id}': {e}")
        conn.rollback()  # Transaktion bei Fehler zurückrollen
    finally:
        conn.close()

def load_discussion_data_db(user: str = None) -> Dict[str, Any]:
    """
    Lädt Diskussionsdaten aus der Datenbank, optional gefiltert nach einem bestimmten Benutzer.
    """
    conn = sqlite3.connect(DISCUSSION_DB_FILE)
    cursor = conn.cursor()
    discussions = {}
    try:
        if user:
            cursor.execute("SELECT * FROM discussions WHERE user = ?", (user,))
        else:
            cursor.execute("SELECT * FROM discussions")
        rows = cursor.fetchall()
        for row in rows:
            disc_id, topic, agents_json, chat_history_json, summary, user_name, timestamp = row
            agents = json.loads(agents_json) if agents_json else []
            chat_history = json.loads(chat_history_json) if chat_history_json else []
            discussions[disc_id] = {
                "topic": topic,
                "agents": agents,
                "chat_history": chat_history,
                "summary": summary,
                "user": user_name,
                "timestamp": timestamp
            }
    except sqlite3.Error as e:
        logging.error(f"Datenbankfehler beim Laden der Diskussionen: {e}")
    finally:
        conn.close()
    return discussions

def evaluate_response(response: str) -> str:
    """
    Eine einfache Heuristik zur Bewertung der Qualität einer Antwort.
    """
    resp_l = response.lower()
    if "wiederhole mich" in resp_l:
        return "schlechte antwort"
    if "neue perspektive" in resp_l:
        return "gute antwort"
    return "neutral"

# Diskussionen-Bewertungen (Werte werden als verschachteltes Dictionary gespeichert)
discussion_ratings = defaultdict(lambda: defaultdict(dict), load_rating_data())

def rate_agent_response(discussion_id: str, iteration: int, agent_name: str, rating_type: str) -> None:
    """
    Erlaubt das Bewerten einer Agentenantwort (Upvote/Downvote) und speichert die Bewertung.
    """
    global discussion_ratings
    if agent_name not in discussion_ratings[discussion_id][iteration]:
        discussion_ratings[discussion_id][iteration][agent_name] = {"upvotes": 0, "downvotes": 0}
    if rating_type == "upvote":
        discussion_ratings[discussion_id][iteration][agent_name]["upvotes"] += 1
    elif rating_type == "downvote":
        discussion_ratings[discussion_id][iteration][agent_name]["downvotes"] += 1
    save_rating_data(discussion_ratings)  # Aktualisierte Bewertungen speichern

# Gemini API-Funktionen

def generate_pdf_summary_from_bytes(file_bytes: bytes, model: genai.GenerativeModel) -> str:
    """
    Generiert eine Zusammenfassung aus den Bytes einer PDF-Datei.
    """
    try:
        prompt = "Fasse den Inhalt der PDF zusammen. Achte darauf, dass wichtige Daten nicht verloren gehen!"
        response = model.generate_content([prompt, file_bytes])  # Kein spezieller Mime-Type
        return response.text
    except Exception as e:
        logging.error(f"Fehler in generate_pdf_summary_from_bytes: {e}", exc_info=True)
        return "Fehler beim Verarbeiten der PDF."

def generate_image_summary_from_bytes(file_bytes: bytes, mime_type: str, model: genai.GenerativeModel) -> str:
    """
    Generiert eine detaillierte Beschreibung für ein Bild.
    """
    try:
        prompt = "Beschreibe den Inhalt des Bildes detailliert."
        # Erstelle den Inhalt als Liste: Erst das Prompt, dann ein Dictionary mit Mime-Type und Bilddaten
        contents = [prompt, {'mime_type': mime_type, 'data': file_bytes}]
        # Konfiguriere die Ausgabeparameter (max_output_tokens etc.)
        generation_config = genai.GenerationConfig(max_output_tokens=500)
        response = model.generate_content(contents, generation_config=generation_config)
        return response.text
    except Exception as e:
        logging.error(f"Fehler in generate_image_summary_from_bytes: {e}", exc_info=True)
        st.error(f"Fehler in generate_image_summary_from_bytes: {e}")
        return "Fehler beim Verarbeiten des Bildes."

def call_gemini_api(contents: list, model: genai.GenerativeModel) -> Dict[str, str]:
    """
    Führt einen API-Aufruf zur Gemini API aus. Es wird ein Retry-Mechanismus implementiert, um zeitweilige Fehler abzufangen.
    """
    retries = 0
    wait_time = 1
    max_wait_time = 60
    while retries < API_MAX_RETRIES:
        try:
            logging.info(f"Sende Anfrage an Gemini ({model.model_name}): {str(contents)[:100]}... (Versuch {retries + 1})")
            response = model.generate_content(contents=contents)
            if not hasattr(response, "text") or not response.text:
                msg = "Leere Antwort von Gemini API."
                logging.warning(msg)
                return {"response": msg}
            return {"response": response.text}
        except Exception as e:
            err_s = str(e)
            logging.error(f"Gemini API Fehler: {err_s}")
            if "429" in err_s or "quota" in err_s.lower():
                # Fehler aufgrund von API-Rate-Limiting: Retry-Mechanismus
                retries += 1
                if retries >= API_MAX_RETRIES:
                    return {"response": "Fehler: Maximale Anzahl an Versuchen erreicht (API-Limit)."}
                wait_time = min(wait_time * 2, max_wait_time)
                actual_wait_time = wait_time * random.uniform(0.5, 1.5)  # Jitter zur Vermeidung von synchronen Anfragen
                logging.warning(f"API-Kontingent erschöpft. Warte {actual_wait_time:.2f} Sekunden...")
                time.sleep(actual_wait_time)
            else:
                return {"response": f"Fehler bei Gemini API Aufruf: {err_s}"}
    return {"response": f"Fehler: Maximale Anzahl an Versuchen erreicht ({API_MAX_RETRIES})."}

def generate_summary(text: str, model: genai.GenerativeModel) -> str:
    """
    Generiert eine prägnante Zusammenfassung des übergebenen Textes.
    """
    prompt = f"Fasse den folgenden Text prägnant zusammen:\n\n{text}"
    result = call_gemini_api([prompt], model=model)
    if SUMMARY_SLEEP_SECONDS > 0:
        time.sleep(SUMMARY_SLEEP_SECONDS)
    return result.get("response", "Fehler: Keine Zusammenfassung generiert.")

def process_uploaded_file(uploaded_file, text_model, vision_model) -> str:
    """
    Verarbeitet hochgeladene Dateien. Unterscheidung zwischen PDF und Bild erfolgt mittels Pattern Matching.
    Vor jedem Lesevorgang wird der Dateizeiger mit seek(0) zurückgesetzt.
    """
    if uploaded_file is None:
        return "Start der Konversation."
    try:
        # Setze den Dateizeiger zurück und lese die Datei
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        mime_type = uploaded_file.type
        
        # Verwende strukturelles Pattern Matching, um den Mime-Type zu prüfen
        match mime_type:
            case "application/pdf":
                return generate_pdf_summary_from_bytes(file_bytes, text_model)
            case _ if mime_type.startswith("image"):
                return generate_image_summary_from_bytes(file_bytes, mime_type, vision_model)
            case _:
                logging.warning(f"Nicht unterstützter Dateityp: {mime_type}")
                return f"Nicht unterstützter Dateityp: {mime_type}"
    except Exception as e:
        logging.error(f"Fehler beim Verarbeiten der Datei: {e}", exc_info=True)
        return "Fehler beim Verarbeiten der Datei."

def joint_conversation_with_selected_agents(
    conversation_topic: str,
    selected_agents: List[Dict[str, str]],
    iterations: int,
    expertise_level: str,
    language: str,
    chat_history: List[Dict[str, str]],
    user_state: str,
    discussion_id: str = None,
    text_model: genai.GenerativeModel = None,
    vision_model: genai.GenerativeModel = None,
    uploaded_file = None
) -> Tuple[List[Dict[str, str]], str, str, Union[int, None], Union[str, None]]:
    """
    Führt die Agenten-Konversation durch. Dabei wird der aktuelle Chatverlauf, die Zusammenfassungen und
    die API-Aufrufe verwaltet. Wichtig: Bei Verwendung von uploaded_file wird der Dateizeiger vor jedem
    Lesevorgang mit uploaded_file.seek(0) zurückgesetzt, um den Fehler 'Unable to process input image' zu vermeiden.
    """
    if discussion_id is None:
        discussion_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_history_filename = f"chat_history_{discussion_id}.txt"

    active_agents_names = [agent["name"] for agent in selected_agents]
    num_agents = len(active_agents_names)
    agent_outputs = [""] * num_agents
    topic_changed = False

    logging.info(f"Konversation gestartet: {active_agents_names}, Iterationen: {iterations}, Diskussions-ID: {discussion_id}")

    # Initiale Zusammenfassung wird vor der Schleife erstellt
    initial_summary = process_uploaded_file(uploaded_file, text_model, vision_model)
    current_summary = initial_summary

    for i in range(iterations):
        agent_idx = i % num_agents
        current_agent_name = active_agents_names[agent_idx]
        current_agent_config = next((agent for agent in selected_agents if agent["name"] == current_agent_name), None)
        current_personality = current_agent_config.get("personality", "neutral")
        current_instruction = current_agent_config.get("instruction", "")

        prompt_text = (
            f"Wir führen eine Konversation über: '{conversation_topic}'.\n" +
            (f"Zusätzliche Informationen: '{initial_summary}'.\n" if initial_summary else "") +
            f"Hier ist die Zusammenfassung der bisherigen Diskussion:\n{current_summary}\n\n" +
            f"Iteration {i+1}: Agent {current_agent_name}, bitte antworte. {current_instruction}\n"
        )
        if i > 0:
            prompt_text += f"Der vorherige Agent sagte: {agent_outputs[(agent_idx - 1) % num_agents]}\n"

        # Persönlichkeitsspezifische Anpassungen
        if current_personality == "kritisch":
            prompt_text += "\nSei besonders kritisch."
        elif current_personality == "visionär":
            prompt_text += "\nSei besonders visionär."
        elif current_personality == "konservativ":
            prompt_text += "\nSei besonders konservativ."
        prompt_text += f"\n\nAntworte auf {language}."

        # Erstelle die Inhaltsliste für den API-Aufruf
        contents = [prompt_text]
        if uploaded_file is not None:
            try:
                # Setze den Dateizeiger zurück und lese die Datei erneut
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                mime_type = uploaded_file.type
                match mime_type:
                    case _ if mime_type.startswith("image"):
                        contents.append({
                            'mime_type': mime_type,
                            'data': file_bytes
                        })
                    case "application/pdf":
                        contents.append(file_bytes)  # Für PDF wird kein zusätzlicher Mime-Type benötigt
                    case _:
                        logging.warning(f"Nicht unterstützter Dateityp in der Konversation: {mime_type}")
            except Exception as e:
                logging.error(f"Fehler beim Lesen der Datei (Iteration {i+1}): {e}", exc_info=True)
                yield chat_history, f"Fehler beim Lesen der Datei (Iteration {i+1}).", discussion_id, (i + 1), current_agent_name
                continue

        # API-Aufruf an Gemini (immer das Textmodell verwenden)
        api_resp = call_gemini_api(contents, model=text_model)
        agent_output = api_resp.get("response", f"Keine Antwort von {current_agent_name}")
        agent_outputs[agent_idx] = agent_output

        # Aktualisiere den Chatverlauf
        chat_history.append({"role": "user", "content": f"Agent {current_agent_name} (Iteration {i + 1}): {prompt_text}"})
        chat_history.append({"role": "assistant", "content": f"{agent_output}"})

        try:
            with open(chat_history_filename, "w", encoding="utf-8") as f:
                for message in chat_history:
                    f.write(f"{message['role']}: {message['content']}\n")
        except IOError as e:
            logging.error(f"Fehler beim Schreiben in Chatverlauf-Datei: {e}")

        # Neue Zusammenfassung basierend auf der letzten Antwort
        new_summary_input = f"Bisherige Zusammenfassung:\n{current_summary}\n\nNeue Antwort von {current_agent_name}:\n{agent_output}"
        current_summary = generate_summary(new_summary_input, model=text_model)
        time.sleep(API_SLEEP_SECONDS)

        # Bewertung der Antwort
        qual = evaluate_response(agent_output)
        if qual == "schlechte antwort":
            logging.info(f"{current_agent_name} => 'schlechte antwort', retry...")
            retry_contents = ["Versuche eine kreativere Antwort."]
            if uploaded_file is not None:
                try:
                    uploaded_file.seek(0)
                    file_bytes = uploaded_file.read()
                    mime_type = uploaded_file.type
                    match mime_type:
                        case _ if mime_type.startswith("image"):
                            retry_contents = [
                                "Versuche eine kreativere Antwort.",
                                {'mime_type': mime_type, 'data': file_bytes}
                            ]
                        case "application/pdf":
                            retry_contents = ["Versuche eine kreativere Antwort.", file_bytes]
                except Exception as e:
                    logging.error(f"Fehler beim Lesen der Datei für Retry: {e}", exc_info=True)
                    yield chat_history, "Fehler beim Lesen der Datei während des Retrys.", discussion_id, (i + 1), current_agent_name
                    continue
            retry_resp = call_gemini_api(retry_contents, model=text_model)
            retry_output = retry_resp.get("response", f"Keine Retry-Antwort von {current_agent_name}")
            if "Fehler" not in retry_output:
                agent_output = retry_output
            agent_outputs[agent_idx] = agent_output

        st.session_state['rating_info']["discussion_id"] = discussion_id
        st.session_state['rating_info']["iteration"] = i + 1
        st.session_state['rating_info']["agent_name"] = current_agent_name

        logging.info(f"Antwort Agent {current_agent_name} (i={i+1}): {agent_output[:50]}...")
        formatted_output_chunk = (
            f"**Iteration {i+1}: Agent {current_agent_name} ({current_personality})**\n\n"
            f"{agent_output}\n\n"
            "---\n\n"
        )
        yield chat_history, formatted_output_chunk, discussion_id, (i + 1), current_agent_name

        # Falls sich das Thema wiederholt, kann ein Themenwechsel erfolgen
        if i > iterations * 0.6 and agent_output == agent_outputs[(agent_idx - 1) % num_agents] and not topic_changed:
            new_topic = "Neues Thema: KI-Trends 2026"
            contents = [new_topic]
            if uploaded_file is not None:
                try:
                    uploaded_file.seek(0)
                    file_bytes = uploaded_file.read()
                    mime_type = uploaded_file.type
                    match mime_type:
                        case _ if mime_type.startswith("image"):
                            contents.append({'mime_type': mime_type, 'data': file_bytes})
                        case "application/pdf":
                            contents.append(file_bytes)
                except Exception as e:
                    logging.error(f"Fehler beim Lesen der Datei für neues Thema: {e}", exc_info=True)
                    yield chat_history, "Fehler beim Lesen der Datei beim Themenwechsel.", discussion_id, (i+1), current_agent_name
                    continue
            agent_outputs = [new_topic] * num_agents  # Zurücksetzen der Agenten-Outputs
            topic_changed = True

    # Finale Zusammenfassung basierend auf dem gesamten Chatverlauf
    final_summary_input = "Gesamter Chatverlauf:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
    final_summary = generate_summary(final_summary_input, model=text_model)
    chat_history.append({"role": "assistant", "content": f"**Gesamtzusammenfassung**:\n{final_summary}"})

    if user_state:
        save_discussion_data_db(discussion_id, conversation_topic, active_agents_names, chat_history, final_summary, user_state)
        logging.info(f"Diskussion {discussion_id} gespeichert.")
    else:
        logging.info("Diskussion nicht gespeichert (kein Benutzer).")

    final_text = agent_outputs[-1]
    chat_history.append({"role": "assistant", "content": f"Finale Aussage:\n{final_text}"})
    logging.info(f"Finale Aussage: {final_text}")
    yield chat_history, final_summary, discussion_id, None, None

def save_chat_as_word(chat_history: List[Dict], discussion_id: str) -> Union[str, None]:
    """
    Speichert den Chatverlauf als Word-Dokument.
    """
    document = Document()
    document.add_heading(f'Agenten-Diskussion: {discussion_id}', level=1)
    for message in chat_history:
        document.add_paragraph(f"{message['role']}: {message['content']}", style='List Bullet')
    filename = f"Diskussion_{discussion_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    try:
        document.save(filename)
        logging.info(f"Word-Datei '{filename}' gespeichert.")
        return filename
    except Exception as e:
        logging.error(f"Fehler beim Speichern der Word-Datei: {e}")
        return None

# Streamlit-App (Benutzeroberfläche)
def main():
    """
    Hauptfunktion der Streamlit-Anwendung zur Darstellung der Benutzeroberfläche.
    """
    st.title("CipherCore Agenten-Konversation")
    st.markdown("AI-THINK-TANK – Die KI-Plattform für bahnbrechende Innovationen.")
    st.markdown("Ein Bild, eine Idee – und in Minuten entsteht eine visionäre Lösung.")

    # Initialisiere Session-State-Variablen, falls sie noch nicht gesetzt sind
    if 'user_state' not in st.session_state:
        st.session_state['user_state'] = None
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'discussion_id' not in st.session_state:
        st.session_state['discussion_id'] = None
    if 'rating_info' not in st.session_state:
        st.session_state['rating_info'] = {}
    if 'formatted_output_text' not in st.session_state:
        st.session_state['formatted_output_text'] = ""
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ""
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None

    st.sidebar.header("API-Schlüssel")
    api_key_input = st.sidebar.text_input("Geben Sie Ihren Gemini API-Schlüssel ein:", type="password", value=st.session_state['api_key'])
    if api_key_input:
        st.session_state['api_key'] = api_key_input

    api_key = st.session_state['api_key']

    # Modelle initialisieren, falls ein API-Schlüssel vorhanden ist
    if api_key:
        genai.configure(api_key=api_key)
        model_text = genai.GenerativeModel(MODEL_NAME_TEXT)
        model_vision = genai.GenerativeModel(MODEL_NAME_VISION)
    else:
        model_text = None
        model_vision = None
        st.warning("Bitte geben Sie einen API-Schlüssel ein, um die Anwendung zu nutzen.")

    # Login/Registrierung
    with st.expander("Login / Registrierung"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Login")
            username_login = st.text_input("Nutzername", key="username_login")
            password_login = st.text_input("Passwort", type="password", key="password_login")
            login_btn = st.button("Login")
            login_status = st.empty()
            if login_btn:
                msg, logged_in_user = login_user(username_login, password_login)
                if logged_in_user:
                    st.session_state['user_state'] = logged_in_user
                    login_status.success(msg)
                    st.rerun()
                else:
                    login_status.error(msg)
        with col2:
            st.subheader("Registrierung")
            username_register = st.text_input("Nutzername", key="username_register")
            password_register = st.text_input("Passwort", type="password", key="password_register")
            register_btn = st.button("Registrieren")
            register_status = st.empty()
            if register_btn:
                msg = register_user(username_register, password_register)
                register_status.info(msg)

    st.markdown("---")
    agent_config_data = load_agent_config()
    agent_selections = {}
    st.subheader("Agenten Auswahl")
    with st.expander("Agenten Auswahl"):
        for agent_data in agent_config_data:
            agent_selections[agent_data["name"]] = {
                "selected": st.checkbox(agent_data["name"]),
                "personality": st.radio(
                    f"Persönlichkeit für {agent_data['name']}",
                    ["kritisch", "visionär", "konservativ", "neutral"],
                    horizontal=True,
                    key=f"personality_{agent_data['name']}"
                )
            }

    topic_input = st.text_input("Diskussionsthema")
    iteration_slider = st.slider("Anzahl Gesprächsrunden", 1, 50, 10)
    level_radio = st.radio("Experten-Level", ["Beginner", "Fortgeschritten", "Experte"], horizontal=True)
    lang_radio = st.radio("Sprache", ["Deutsch", "Englisch", "Französisch", "Spanisch"], horizontal=True)

    st.subheader("Datei hochladen (optional)")
    uploaded_file = st.file_uploader("Datei auswählen (PDF, PNG, JPG, JPEG, GIF)", type=["pdf", "png", "jpg", "jpeg", "gif"])
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        file_type = uploaded_file.type
        st.write(f"Hochgeladener Dateityp: {file_type}")
        if file_type.startswith("image"):
            st.image(uploaded_file)
        elif file_type == "application/pdf":
            st.write("PDF-Datei hochgeladen (Vorschau nicht unterstützt)")
        else:
            st.write("Datei hochgeladen")

    with st.expander("Gespeicherte Diskussionen"):
        load_disc_btn = st.button("Diskussionen laden")
        saved_discussions = st.empty()
        if load_disc_btn:
            if st.session_state['user_state']:
                disc_data = load_discussion_data_db(st.session_state['user_state'])
                saved_discussions.json(disc_data)
            else:
                saved_discussions.warning("Bitte zuerst einloggen.")

    start_btn = st.button("Konversation starten")

    st.subheader("Agenten-Konversation")
    for message in st.session_state['chat_history']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.subheader("Formatierter Output")
    st.markdown(st.session_state['formatted_output_text'])

    # Bewertungs-Buttons (Upvote/Downvote)
    rating_col1, rating_col2, rating_col3 = st.columns([1, 1, 3])
    if st.session_state['rating_info'].get("iteration") is not None:
        with rating_col1:
            upvote_btn = st.button("👍 Upvote")
        with rating_col2:
            downvote_btn = st.button("👎 Downvote")
        with rating_col3:
            rating_label = st.empty()
        if upvote_btn:
            did = st.session_state['rating_info'].get("discussion_id")
            itn = st.session_state['rating_info'].get("iteration")
            agn = st.session_state['rating_info'].get("agent_name")
            if did and itn and agn:
                rate_agent_response(did, itn, agn, "upvote")
                rating_label.success("👍")
            else:
                rating_label.error("Fehler (Upvote).")
        if downvote_btn:
            did = st.session_state['rating_info'].get("discussion_id")
            itn = st.session_state['rating_info'].get("iteration")
            agn = st.session_state['rating_info'].get("agent_name")
            if did and itn and agn:
                rate_agent_response(did, itn, agn, "downvote")
                rating_label.success("👎")
            else:
                rating_label.error("Fehler (Downvote).")

    save_col1, save_col2 = st.columns(2)
    with save_col1:
        save_btn = st.button("Diskussion speichern")
        save_status = st.empty()
        if save_btn:
            if st.session_state['user_state']:
                active_agents_names = [agent['name'] for agent in agent_config_data if agent_selections[agent['name']]['selected']]
                save_discussion_data_db(st.session_state['discussion_id'], topic_input, active_agents_names,
                                          st.session_state['chat_history'], "Manuell gespeichert", st.session_state['user_state'])
                save_status.success("Diskussion in Datenbank gespeichert.")
            else:
                save_status.warning("Bitte zuerst einloggen.")
    with save_col2:
        word_save_btn = st.button("Chat als Word speichern")
        if word_save_btn:
            if st.session_state['discussion_id']:
                word_filename = save_chat_as_word(st.session_state['chat_history'], st.session_state['discussion_id'])
                if word_filename:
                    with open(word_filename, "rb") as file:
                        st.download_button(
                            label="Word-Datei herunterladen",
                            data=file,
                            file_name=word_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Fehler beim Erstellen der Word-Datei.")
            else:
                st.warning("Diskussions-ID fehlt. Starten Sie zuerst eine Konversation.")

    # Hauptteil: Starten der Konversation
    if start_btn:
        selected_agents = [
            {"name": agent, "personality": agent_selections[agent]["personality"],
             "instruction": next((a["description"] for a in agent_config_data if a["name"] == agent), "")}
            for agent in agent_selections if agent_selections[agent]["selected"]
        ]
        if not selected_agents:
            st.warning("Bitte wähle mindestens einen Agenten aus.")
        elif not api_key:
            st.warning("Bitte geben Sie einen API-Schlüssel ein.")
        else:
            st.session_state['chat_history'] = []
            st.session_state['formatted_output_text'] = ""
            st.session_state['discussion_id'] = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state['rating_info'] = {}
            try:
                with st.spinner("Konversation wird gestartet..."):
                    agent_convo = joint_conversation_with_selected_agents(
                        conversation_topic=topic_input,
                        selected_agents=selected_agents,
                        iterations=iteration_slider,
                        expertise_level=level_radio,
                        language=lang_radio,
                        chat_history=[],
                        user_state=st.session_state['user_state'],
                        discussion_id=st.session_state['discussion_id'],
                        text_model=model_text,
                        vision_model=model_vision,
                        uploaded_file=st.session_state.get('uploaded_file')
                    )
                    for updated_hist, chunk_text, disc_id, iteration_num, agent_n in agent_convo:
                        st.session_state['discussion_id'] = disc_id
                        st.session_state['rating_info']["discussion_id"] = disc_id
                        st.session_state['rating_info']["iteration"] = iteration_num
                        st.session_state['rating_info']["agent_name"] = agent_n

                        if updated_hist and len(updated_hist) > len(st.session_state['chat_history']):
                            new_messages = updated_hist[len(st.session_state['chat_history']):]
                            for message in new_messages:
                                st.session_state['chat_history'].append(message)
                                with st.chat_message(message["role"]):
                                    st.markdown(message["content"])
                            st.session_state['formatted_output_text'] += chunk_text

            except (tornado.websocket.WebSocketClosedError, tornado.iostream.StreamClosedError) as e:
                st.error(f"Verbindungsfehler: {e}. Bitte versuche es später erneut.")
                logging.exception("Verbindungsfehler in der Hauptschleife:")
            except StopCandidateException as e:
                st.error(f"Die Konversation wurde unerwartet beendet: {e}")
                logging.exception("StopCandidateException in Hauptschleife:")
            except Exception as e:
                st.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
                logging.exception("Unerwarteter Fehler in der Hauptschleife:")

if __name__ == "__main__":
    main()
