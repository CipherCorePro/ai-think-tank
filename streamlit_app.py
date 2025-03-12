import re
import logging
import datetime
import json
import hashlib
import os
import time
from collections import defaultdict
from typing import List, Dict, Tuple, Any
import sqlite3
from jsonschema import validate, ValidationError
from docx import Document
from docx.shared import Inches

from dotenv import load_dotenv
from google import genai

import streamlit as st

# ---------------------------
# 1) Konfiguration und Setup
# ---------------------------
#load_dotenv() # No longer loading from .env, getting from user input.

#API_KEY = os.getenv("API_KEY") # Removed, we'll get it from Streamlit.
MODEL_NAME = "gemini-2.0-flash-thinking-exp-01-21"

#if not API_KEY: #Moved this check to within main() to use API_KEY set by user
#    raise ValueError("API_KEY nicht in .env gefunden!")

#client = genai.Client(api_key=API_KEY) #Initialized in main() with user-provided key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_SLEEP_SECONDS = 10
API_MAX_RETRIES = 3

AUDIT_LOG_FILE = "audit_log.txt"
EXPIRATION_TIME_SECONDS = 300
ROLE_PERMISSIONS = {
    "user": ["REQ", "DATA"],
    "admin": ["REQ", "DATA", "CALC", "IF", "AI"]
}
PRIORITY_MAP = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}

# ---------------------------
# 2) Nutzer-Login-System (JSON & Validierung)
# ---------------------------
USER_DATA_FILE = "user_data.json"
DISCUSSION_DB_FILE = "discussion_data.db"
RATING_DATA_FILE = "rating_data.json"
AGENT_CONFIG_FILE = "agent_config.json"

USER_DATA_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
            "type": "object",
            "properties": {
                "password": {"type": "string"}
            },
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


def load_json_data(filename: str, schema: dict = None) -> Dict[str, Any]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if schema:
                validate(instance=data, schema=schema)
            return data
    except FileNotFoundError:
        logging.warning(f"Datei '{filename}' nicht gefunden. Starte mit leeren Daten.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Fehler beim Lesen von '{filename}': Ungültiges JSON-Format. Details: {e}")
        return {}
    except ValidationError as e:
        logging.error(f"Datei '{filename}' entspricht nicht dem erwarteten Schema: {e}")
        return {}

def save_json_data(data: Dict[str, Any], filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logging.error(f"Fehler beim Schreiben in Datei '{filename}': {e}")


def load_user_data() -> Dict[str, Any]:
    return load_json_data(USER_DATA_FILE, USER_DATA_SCHEMA)

def save_user_data(user_data: Dict[str, Any]) -> None:
    save_json_data(user_data, USER_DATA_FILE)

def load_rating_data() -> Dict[str, Any]:
    return load_json_data(RATING_DATA_FILE)

def save_rating_data(rating_data: Dict[str, Any]) -> None:
    save_json_data(rating_data, RATING_DATA_FILE)

def load_agent_config() -> List[Dict[str, str]]:
    config = load_json_data(AGENT_CONFIG_FILE, AGENT_CONFIG_SCHEMA)
    if not isinstance(config, list):
        logging.error(f"Agentenkonfiguration in '{AGENT_CONFIG_FILE}' ist ungültig oder leer. Stelle sicher, dass es eine Liste ist.")
        return []
    return config


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def register_user(username: str, password: str) -> str:
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return "Ungültiger Nutzername. Nur Buchstaben, Zahlen, '-', '_' erlaubt."
    if len(password) < 8:
        return "Passwort muss mindestens 8 Zeichen lang sein."

    user_data = load_user_data()
    if username in user_data:
        return "Nutzername bereits vergeben."
    user_data[username] = {"password": hash_password(password)}
    save_user_data(user_data)
    return "Registrierung erfolgreich."

def login_user(username: str, password: str) -> Tuple[str, str]:
    """ Gibt (Meldung, username_oder_None) zurück """
    user_data = load_user_data()
    if username in user_data and verify_password(password, user_data[username]["password"]):
        return "Login erfolgreich.", username
    return "Login fehlgeschlagen.", None

# ---------------------------
# 3) Datenbank-Interaktion (SQLite für Diskussionen)
# ---------------------------
def create_discussion_table():
    """ Erstellt die Diskussionstabelle, falls nicht vorhanden. """
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

create_discussion_table()

def save_discussion_data_db(discussion_id: str, topic: str, agents: List[str], chat_history: List[Dict], summary: str, user: str = None) -> None:
    """ Speichert Diskussionsdaten in der SQLite Datenbank. """
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
        conn.rollback()
    finally:
        conn.close()

def load_discussion_data_db(user: str = None) -> Dict[str, Any]:
    """ Lädt Diskussionsdaten aus der SQLite Datenbank. Optional für einen bestimmten Nutzer. """
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


# ---------------------------
# 4) Bewertung der Antwort
# ---------------------------
def evaluate_response(response: str) -> str:
    resp_l = response.lower()
    if "wiederhole mich" in resp_l:
        return "schlechte antwort"
    elif "neue perspektive" in resp_l:
        return "gute antwort"
    else:
        return "neutral"

# ---------------------------
# 5) Up-/Downvotes
# ---------------------------
discussion_ratings = defaultdict(lambda: defaultdict(dict), load_rating_data())

def rate_agent_response(discussion_id: str, iteration: int, agent_name: str, rating_type: str) -> None:
    """
    Verhindert KeyError, indem wir (discussion_id, iteration, agent_name) bei Bedarf anlegen.
    """
    global discussion_ratings
    if agent_name not in discussion_ratings[discussion_id][iteration]:
        discussion_ratings[discussion_id][iteration][agent_name] = {"upvotes": 0, "downvotes": 0}

    if rating_type == "upvote":
        discussion_ratings[discussion_id][iteration][agent_name]["upvotes"] += 1
    elif rating_type == "downvote":
        discussion_ratings[discussion_id][iteration][agent_name]["downvotes"] += 1

    save_rating_data(discussion_ratings)

# ---------------------------
# 6) Gemini-API mit Retry, Backoff & Fehleranalyse
# ---------------------------
def call_gemini_api(prompt: str, api_key: str) -> Dict[str, str]:
    """
    Ruft die Gemini-API auf mit erweitertem Retry-Mechanismus und Fehlerbehandlung.
    """

    client = genai.Client(api_key=api_key)  # Use API key passed into the function

    retry_delay = API_SLEEP_SECONDS
    for attempt in range(API_MAX_RETRIES + 1):
        try:
            logging.info(f"[{attempt+1}/{API_MAX_RETRIES+1}] Sende Prompt an Gemini: {prompt[:100]}...")
            response = client.models.generate_content(model=MODEL_NAME, contents=[prompt])

            # Wartezeit nach jedem Request
            time.sleep(API_SLEEP_SECONDS)

            if not hasattr(response, "text") or not response.text:
                msg = "Leere Antwort von Gemini API."
                logging.warning(msg)
                return {"response": msg}

            return {"response": response.text}

        except genai.APIError as e:
            err_s = str(e)
            logging.error(f"Gemini API Fehler (Versuch {attempt+1}): {err_s}, Status Code: {e.status_code}")

            if e.status_code == 429:
                if attempt < API_MAX_RETRIES:
                    retry_delay *= 2
                    logging.info(f"Rate Limit erreicht. Warte {retry_delay}s und versuche erneut.")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {"response": f"API Rate Limit erreicht nach mehreren Versuchen. Bitte später erneut versuchen."}
            elif e.status_code == 503:
                if attempt < API_MAX_RETRIES:
                    logging.info(f"Server überlastet. Warte {retry_delay}s und versuche erneut.")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {"response": "Gemini API Server überlastet nach mehreren Versuchen."}
            elif e.status_code == 401:
                return {"response": "Authentifizierungsfehler bei der Gemini API. Überprüfen Sie den API-Schlüssel."}
            else:
                if attempt < API_MAX_RETRIES:
                    logging.info(f"Unerwarteter API Fehler, versuche Retry. Warte {retry_delay}s.")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {"response": f"Unerwarteter Fehler bei Gemini API Aufruf nach mehreren Versuchen: {err_s}"}
        except Exception as e:
            err_s = str(e)
            logging.error(f"Genereller Fehler bei Gemini API Aufruf (Versuch {attempt+1}): {err_s}")
            return {"response": f"Fehler bei Gemini API Aufruf: {err_s}"}

    return {"response": "Unbekannter Fehler nach mehreren API-Versuchen."}


# ---------------------------
# 7) Generator-Funktion (Alle Agenten, kein Diagramm)
# ---------------------------
def joint_conversation_with_selected_agents(
    conversation_topic: str,
    selected_agents: List[Dict[str, str]],
    iterations: int,
    expertise_level: str,
    language: str,
    chat_history: List[Dict[str, str]],
    user_state: str,
    discussion_id: str = None,
    api_key: str = None
):
    """
    user_state: der eingeloggte Nutzername (oder None).
    """
    if discussion_id is None:
        discussion_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    active_agents_names = [sa["name"] for sa in selected_agents]
    num_agents = len(active_agents_names)
    agent_outputs = [""] * num_agents
    topic_changed = False

    logging.info(f"Konversation gestartet: {active_agents_names}, iters={iterations}, level={expertise_level}, lang={language}, Diskussions-ID: {discussion_id}")

    for i in range(iterations):
        agent_idx = i % num_agents
        current_agent_name = active_agents_names[agent_idx]
        current_agent_config = next((a for a in selected_agents if a["name"] == current_agent_name), None)
        current_personality = current_agent_config.get("personality", "neutral")
        current_instruction = current_agent_config.get("instruction", "")

        prev_agent_name = active_agents_names[(agent_idx - 1) % num_agents]
        prev_output = agent_outputs[(agent_idx - 1) % num_agents]

        prompt_txt = (
            f"Wir führen eine Konversation über: '{conversation_topic}'.\n"
            f"Iteration {i+1}: Agent {current_agent_name} (Spezialist für **{current_agent_name}**). {current_instruction}\n"
            f"Agent {prev_agent_name} sagte: {prev_output}\n"
        )

        if current_personality == "kritisch":
            prompt_txt += "\nSei kritisch und hinterfrage Annahmen."
        elif current_personality == "visionär":
            prompt_txt += "\nSei visionär und denke groß."
        elif current_personality == "konservativ":
            prompt_txt += "\nSei konservativ und bleibe bei Bewährtem."

        if language == "Deutsch":
            prompt_txt += "\n\nAntworte auf Deutsch."
        elif language == "Englisch":
            prompt_txt += "\n\nRespond in English."
        elif language == "Französisch":
            prompt_txt += "\n\nRépondez en français."
        elif language == "Spanisch":
            prompt_txt += "\n\nResponde en español."

        chat_history.append({
            "role": "user",
            "content": f"Agent {current_agent_name} (Iteration {i+1}): Thema {conversation_topic}, vorheriger: {prev_agent_name}: {prev_output}"
        })

        api_resp = call_gemini_api(prompt_txt, api_key)  # Pass the API key to the API call function
        agent_output = api_resp.get("response", f"Keine Antwort von {current_agent_name}")
        agent_outputs[agent_idx] = agent_output

        qual = evaluate_response(agent_output)
        if qual == "schlechte antwort":
            logging.info(f"{current_agent_name} => 'schlechte antwort', retry ...")
            retry_resp = call_gemini_api("Versuche eine kreativere Antwort.", api_key)  # Pass the API key
            retry_output = retry_resp.get("response", f"Keine Retry-Antwort von {current_agent_name}")
            if "Fehler bei Gemini API Aufruf" not in retry_output:
                agent_output = retry_output
            agent_outputs[agent_idx] = agent_output

        chat_history.append({
            "role": "assistant",
            "content": f"Antwort von Agent {current_agent_name} (Iteration {i+1}):\n{agent_output}"
        })
        logging.info(f"Antwort Agent {current_agent_name} (i={i+1}): {agent_output}")

        formatted_output_chunk = (
            f"**Iteration {i+1}: Agent {current_agent_name} ({current_personality})**\n\n"
            f"{agent_output}\n\n"
            "---\n\n"
        )

        yield chat_history, formatted_output_chunk, discussion_id, (i+1), current_agent_name

        if i > (iterations * 0.6) and agent_output == agent_outputs[(agent_idx - 1) % num_agents] and not topic_changed:
            new_topic = "Neues Thema: KI-Trends 2026"
            agent_outputs = [new_topic] * num_agents
            topic_changed = True

    sum_prompt = f"Fasse die gesamte Diskussion über '{conversation_topic}' zusammen."
    sum_resp = call_gemini_api(sum_prompt, api_key)  # Pass the API key
    sum_text = sum_resp.get("response", "Keine Zusammenfassung generiert.")
    chat_history.append({
        "role": "assistant",
        "content": f"**Zusammenfassung**:\n{sum_text}"
    })

    if user_state:
        save_discussion_data_db(discussion_id, conversation_topic, active_agents_names, chat_history, sum_text, user_state)
        logging.info(f"Diskussion {discussion_id} für {user_state} in Datenbank gespeichert.")
    else:
        logging.info("Keine Speicherung in Datenbank, kein Benutzer eingeloggt.")

    final_text = agent_outputs[-1]
    chat_history.append({
        "role": "assistant",
        "content": f"Finale Aussage:\n{final_text}"
    })

    logging.info(f"Finale Aussage: {final_text}")

    yield chat_history, sum_text, discussion_id, None, None

# ---------------------------
# 8) Funktion zum Speichern als Word-Datei
# ---------------------------
def save_chat_as_word(chat_history: List[Dict], discussion_id: str) -> str:
    """Speichert den Chatverlauf als formatierte Word-Datei."""
    document = Document()
    document.add_heading(f'CipherCore Agenten-Diskussion: {discussion_id}', level=1)

    for message in chat_history:
        role = message['role']
        content = message['content']
        if role == 'user':
            document.add_paragraph(f"Nutzer:", style='List Bullet').add_run(f" {content}").bold = True
        elif role == 'assistant':
            agent_name_match = re.search(r'Agent (.*?)\s', content) # Agentennamen extrahieren
            agent_name = agent_name_match.group(1) if agent_name_match else "Agent"
            p = document.add_paragraph(f"{agent_name}:", style='List Bullet')
            p.add_run(f" {content.split(':\n', 1)[1] if ':\n' in content else content}") # Antwortinhalt extrahieren

    filename = f"CipherCore_Diskussion_{discussion_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    try:
        document.save(filename)
        logging.info(f"Word-Datei '{filename}' erfolgreich gespeichert.")
        return filename
    except Exception as e:
        logging.error(f"Fehler beim Speichern der Word-Datei: {e}")
        return None # Fehlerfall signalisieren

# ---------------------------
# 9) Streamlit App ohne Diagramm - DYNAMISCH mit agent_config.json
# ---------------------------

def main():
    st.title("CipherCore Agenten-Konversation")
    st.markdown("Willkommen bei CipherCore! Ihre Plattform für sichere Programmierung und innovative KI-Lösungen.")
    st.markdown("Dieses Tool demonstriert eine Konversation zwischen verschiedenen KI-Agenten, die von CipherCore für Sie entwickelt wurden. Wählen Sie Agenten aus, geben Sie ein Thema vor und starten Sie die Diskussion. Wir bei CipherCore legen größten Wert auf Sicherheit und Innovation in allen unseren Lösungen.")

    # Initialize session state for user
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
        st.session_state['api_key'] = None


    # API Key Input
    st.sidebar.header("API-Schlüssel")
    api_key = st.sidebar.text_input("Geben Sie Ihren Gemini API-Schlüssel ein:", type="password")


    if not api_key:
        st.warning("Bitte geben Sie einen API-Schlüssel ein, um die Anwendung zu nutzen.")
        return # Stop execution if no API key is provided
    else:
        st.session_state['api_key'] = api_key #Store the API Key to use in the function


    # Login/Registration Section
    with st.expander("Login / Registrierung", expanded=False):
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
                    st.success(f"Eingeloggt als: {st.session_state['user_state']}")
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

    # Agent Selection and Configuration
    agent_config_data = load_agent_config()
    agent_selections = {}
    st.subheader("Agenten Auswahl")
    with st.expander("Agenten Auswahl (auf-/zuklappbar)", expanded=False):
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

    # Input Fields
    topic_input = st.text_input("Diskussionsthema")
    iteration_slider = st.slider("Anzahl Gesprächsrunden", 20, 100, value=10, step=1)
    level_radio = st.radio("Experten-Level", ["Beginner", "Fortgeschritten", "Experte"], horizontal=True)
    lang_radio = st.radio("Sprache", ["Deutsch", "Englisch", "Französisch", "Spanisch"], horizontal=True)

    # Saved Discussions
    with st.expander("Gespeicherte Diskussionen", expanded=False):
        load_disc_btn = st.button("Diskussionen laden")
        saved_discussions = st.empty()

        if load_disc_btn:
            if st.session_state['user_state']:
                disc_data = load_discussion_data_db(st.session_state['user_state'])
                saved_discussions.json(disc_data)
            else:
                saved_discussions.warning("Bitte zuerst einloggen.")

    # Start Conversation Button
    start_btn = st.button("Konversation starten")

    # Chatbot Display
    st.subheader("Agenten-Konversation")
    for message in st.session_state['chat_history']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Formatted Output
    st.subheader("Formatierter Output")
    st.markdown(st.session_state['formatted_output_text'])


    # Rating Section (Initially Hidden)
    rating_col1, rating_col2, rating_col3 = st.columns([1,1,3])  # Adjust the ratio as needed

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
                rating_label.success("👍 Upvote gegeben")
            else:
                rating_label.error("Fehler beim Upvote (fehlende Daten).")

        if downvote_btn:
            did = st.session_state['rating_info'].get("discussion_id")
            itn = st.session_state['rating_info'].get("iteration")
            agn = st.session_state['rating_info'].get("agent_name")
            if did and itn and agn:
                rate_agent_response(did, itn, agn, "downvote")
                rating_label.success("👎 Downvote gegeben")
            else:
                rating_label.error("Fehler beim Downvote (fehlende Daten).")

    # Save Buttons
    save_col1, save_col2 = st.columns(2)

    with save_col1:
        save_btn = st.button("Diskussion speichern")
        save_status = st.empty()

        if save_btn:
            if st.session_state['user_state']:
                active_agents_names = [agent['name'] for agent in agent_config_data if agent_selections[agent['name']]['selected']]
                save_discussion_data_db(st.session_state['discussion_id'], topic_input, active_agents_names, st.session_state['chat_history'], "Manuell gespeichert", st.session_state['user_state'])
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

    # Start Conversation Logic
    if start_btn:
        selected_agents = [
            {"name": agent, "personality": agent_selections[agent]["personality"], "instruction": next((a["description"] for a in agent_config_data if a["name"] == agent), "")}
            for agent in agent_selections
            if agent_selections[agent]["selected"]
        ]

        if not selected_agents:
            st.warning("Bitte wähle mindestens einen Agenten aus.")
        else:
            st.session_state['chat_history'] = []
            st.session_state['formatted_output_text'] = ""
            st.session_state['discussion_id'] = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state['rating_info'] = {}


            agent_convo = joint_conversation_with_selected_agents(
                conversation_topic=topic_input,
                selected_agents=selected_agents,
                iterations=iteration_slider,
                expertise_level=level_radio,
                language=lang_radio,
                chat_history=[],  # Start with an empty chat history
                user_state=st.session_state['user_state'],
                discussion_id=st.session_state['discussion_id'],
                api_key = st.session_state['api_key']  # Pass the API key here
            )

            for updated_hist, chunk_text, disc_id, iteration_num, agent_n in agent_convo:

                st.session_state['discussion_id'] = disc_id
                st.session_state['rating_info']["discussion_id"] = disc_id
                st.session_state['rating_info']["iteration"] = iteration_num
                st.session_state['rating_info']["agent_name"] = agent_n

                # Append new messages to the chat history
                if updated_hist and len(updated_hist) > len(st.session_state['chat_history']):
                    new_messages = updated_hist[len(st.session_state['chat_history']):]
                    for message in new_messages:
                        st.session_state['chat_history'].append(message)
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])


                # Update formatted output text
                st.session_state['formatted_output_text'] += chunk_text
                st.markdown(st.session_state['formatted_output_text']) # Display incrementally

            st.rerun()



if __name__ == "__main__":
    main()
