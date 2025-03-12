# AI-THINK-TANK: A Multilingual AI Agent Conversation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-think-tank-5vtskdnb8xtgvonz4qqgvm.streamlit.app)

[**Live Demo**](https://ai-think-tank-5vtskdnb8xtgvonz4qqgvm.streamlit.app)

## Overview

AI-THINK-TANK is a multilingual web application built with Streamlit that simulates conversations between multiple AI agents powered by Google's Gemini models.  It supports both text-based (`gemini-pro`) and image-based (`gemini-pro-vision`) interactions, enabling rich, dynamic dialogues. Users can configure a diverse team of AI agents, each with unique personalities, assign a discussion topic (optionally providing a PDF or image as context), and observe the collaborative exchange of ideas. The application provides features for user authentication, saving/loading discussions, rating agent responses, and exporting conversations as Word documents. The user interface is available in multiple languages (English, German, Spanish, Russian, Chinese, and French).

## Key Features

*   **Multi-Agent Simulation:** Simulate conversations between multiple AI agents powered by Google's Gemini models.
*   **Configurable Agent Personalities:** Select from pre-defined agents with distinct personalities (critical, visionary, conservative, neutral) or define your own in `agent_config.json`.
*   **Text and Image Input:**  Provide a discussion topic as text, or upload a PDF document or an image (PNG, JPG, JPEG, GIF) to guide the conversation.
*   **Dynamic Prompts:** Prompts to the AI agents are dynamically generated based on the conversation history, selected language, and agent personalities.
*   **Adjustable Parameters:** Control the number of conversation rounds and the expertise level of the agents.
*   **Multilingual Support:** The user interface is available in English, German, Spanish, Russian, Chinese, and French.  The language can be selected via a dropdown in the sidebar.  AI agents respond based on the user-selected language (using language-specific prompts).
*   **User Authentication:** Secure user accounts with login and registration, allowing users to save and load their discussions.
*   **Persistent Storage (SQLite):**  Save conversation histories, user data, and agent ratings in an SQLite database.  (See "Deployment on Streamlit Cloud" for important considerations regarding persistence.)
*   **Response Evaluation:** Rate agent responses with upvotes and downvotes.
*   **Word Document Export:** Export the complete conversation history as a formatted Word document (.docx).
*   **Robust Error Handling:**  Handles API errors, connection issues, and file processing errors gracefully, providing informative messages to the user.
*   **Detailed Logging:** Logs events and errors for debugging and monitoring.
*   **Streamlit Cloud Ready:** Designed for easy deployment on Streamlit Cloud, with instructions for secure API key management.

## Table of Contents

*   [Overview](#overview)
*   [Key Features](#key-features)
*   [Installation](#installation)
*   [Configuration](#configuration)
    *   [API Key](#api-key)
    *   [Agent Configuration (`agent_config.json`)](#agent-configuration-agent_configjson)
    *   [Translations](#translations-multilingual-support)
    *   [Constants](#constants)
*   [Usage](#usage)
*   [Deployment on Streamlit Cloud](#deployment-on-streamlit-cloud)
*   [Architecture](#architecture)
*   [Data Storage](#data-storage)
*   [Troubleshooting](#troubleshooting)
*   [Contributing](#contributing)
*   [License](#license)
*   [Disclaimer](#disclaimer)

## Installation

1.  **Prerequisites:**
    *   Python 3.7+
    *   A Google Cloud account with access to the Gemini API.  [Obtain an API key here](https://aistudio.google.com/apikey).

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    Create a `requirements.txt` file with the following content:

    ```
    streamlit
    google-generativeai
    python-docx
    jsonschema
    tornado
    mimetypes
    ```

3.  **Clone the Repository:**

    ```bash
    git clone <Repository-URL>
    cd <Repository-Name>
    ```

4.  **Run the Application:**

    ```bash
    streamlit run streamlit_app.py
    ```
    (Replace `streamlit_app.py` with the actual name of your main Python file if it's different.)

## Configuration

### API Key

Enter your Gemini API key in the designated field in the Streamlit application's sidebar.  **Crucially**, for security reasons, *never* hardcode your API key directly into the source code.  Instead, use Streamlit's Secrets management (see "Deployment on Streamlit Cloud" below).

### Agent Configuration (`agent_config.json`)

The `agent_config.json` file defines the available AI agents.  It's a JSON array of objects, where each object represents an agent and *must* have the following properties:

*   `name`: (string) The name of the agent.
*   `personality`: (string) The agent's personality.  Must be one of: "kritisch" (critical), "visionär" (visionary), "konservativ" (conservative), "neutral".
*   `description`: (string) A brief description of the agent.

Example:

```json
[
    {
        "name": "AgentA",
        "personality": "kritisch",
        "description": "A critical thinker who questions arguments."
    },
    {
        "name": "AgentB",
        "personality": "visionär",
        "description": "A visionary who brings new ideas and perspectives."
    }
]
```

### Translations (Multilingual Support)

The `translations` dictionary within your main Python file (`streamlit_app.py`) stores the text used in the user interface in multiple languages.  Each language has a sub-dictionary with key-value pairs.  The *keys* are identifiers (e.g., `title`, `login_btn`), and the *values* are the translated strings.

*   **Adding a new language:** Add a new sub-dictionary to `translations` with the appropriate language code (e.g., "fr" for French).  Translate *all* existing keys into the new language.
*   **Adding new UI text:**  Whenever you add new text to the user interface, add a corresponding entry to the `translations` dictionary for *all* supported languages.  Use the `get_translation(lang, key)` function to retrieve the correct text based on the user's selected language.

### Constants

Several constants in your main Python file (`streamlit_app.py`) control the application's behavior:

*   `MODEL_NAME_TEXT`: The name of the Gemini model to use for text generation (e.g., `"gemini-1.5-pro-002"`).  **Use a current, supported model name.**
*   `MODEL_NAME_VISION`: The name of the Gemini model to use for image processing (e.g., `"gemini-1.5-pro-002"`). **Use a current, supported *vision* model name.**
*   `API_SLEEP_SECONDS`: The delay (in seconds) between API calls to avoid rate limits.
*   `API_MAX_RETRIES`: The maximum number of times to retry an API call if it fails.
*   `SUMMARY_SLEEP_SECONDS`:  A delay after generating summaries.
*   `USE_CHAT_HISTORY_FILE`:  Set to `True` to write the chat history to a local `chat_history.txt` file.  Set to `False` to disable this (recommended for Streamlit Cloud deployments).
*   `AUDIT_LOG_FILE`, `EXPIRATION_TIME_SECONDS`, `ROLE_PERMISSIONS`, `PRIORITY_MAP`, `USER_DATA_FILE`, `DISCUSSION_DB_FILE`, `RATING_DATA_FILE`, `AGENT_CONFIG_FILE`:  These constants define filenames, durations, role permissions, and other configuration settings.  Modify these only if you understand their purpose.

## Usage

1.  **Select Language:** Choose your preferred language from the dropdown in the sidebar.
2.  **Login/Register (Optional):** Create a new account or log in to an existing one to save and load your conversations.
3.  **Select Agents:**  Choose the AI agents you want to participate in the conversation.
4.  **Provide Input:**
    *   **Topic (Text):** Enter a discussion topic in the text input field.
    *   **Upload File (Optional):** Upload a PDF document or an image (PNG, JPG, JPEG, GIF) to provide context for the discussion.
5.  **Configure Parameters:** Set the number of conversation rounds.
6.  **Start Conversation:** Click the "Start Conversation" button.
7.  **Interact and Evaluate:** Observe the conversation unfold in the chat interface.  You can upvote or downvote individual agent responses.
8.  **Save/Export:**
    *   **Save:** Save the conversation to the database (requires login).
    *   **Export:** Download the conversation as a formatted Word document.

## Deployment on Streamlit Cloud

1.  **Secrets Management:** **Never store your API key directly in your code.** Use Streamlit Cloud's Secrets management:
    *   In your Streamlit Cloud dashboard, go to your app.
    *   Click the "..." menu and select "Edit Secrets".
    *   Add a secret named `GEMINI_API_KEY` and paste your API key as the value.
    *   In your code, access the key using:
        ```python
        api_key = st.secrets["GEMINI_API_KEY"]
        if not api_key:
            st.warning(get_translation(lang, "api_key_warning"))
            st.stop()  # Or return, as in the provided code
        ```

2.  **Persistence:** Streamlit Cloud uses a *temporary* filesystem.  Files written during the application's execution (including the SQLite database) will *not* persist between restarts.
    *   **For short-term session data:** Use `st.session_state`.
    *   **For long-term persistence:** Use an *external* database service (PostgreSQL, MySQL, MongoDB Atlas, Firebase, Supabase, etc.).  This requires modifying your code to connect to the external database.  *This is highly recommended for any production deployment.*
    *  **Disable `USE_CHAT_HISTORY_FILE`:** set to `False`.

## Architecture

The application consists of the following main components:

*   **`streamlit_app.py` (or your main file):**  Contains the Streamlit user interface, event handling, and overall application logic.
*   **`joint_conversation_with_selected_agents()`:**  The core function that manages the conversation flow, interacts with the Gemini API, and yields updates to the UI.
*   **`call_gemini_api()`:**  Handles communication with the Gemini API, including retries and error handling.
*   **`generate_pdf_summary_from_bytes()`:**  Generates a text summary from a PDF file.
*   **`generate_image_summary_from_bytes()`:**  Generates a description of an image.
*   **`process_uploaded_file()`:**  A helper function to handle both PDF and image uploads.
*   **`generate_summary()`:**  Generates a concise summary of a given text.
*   **`save_chat_as_word()`:**  Exports the conversation history to a Word document.
*   **`load_json_data()`, `save_json_data()`:**  Functions for loading and saving data to JSON files.
*   **`load_user_data()`, `save_user_data()`, `load_rating_data()`, `save_rating_data()`, `load_agent_config()`:** Convenience functions for loading and saving specific data files.
*   **`hash_password()`, `verify_password()`:**  Functions for securely handling user passwords.
*   **`register_user()`, `login_user()`:**  Functions for user registration and login.
*   **`create_discussion_table()`, `save_discussion_data_db()`, `load_discussion_data_db()`:**  Functions for interacting with the SQLite database.
*   **`rate_agent_response()`:**  Handles user ratings of agent responses.
*   **`get_translation()`:** Retrieves the appropriate translation based on the selected language.
*   **`translations` (dictionary):**  Contains all the text used in the UI, translated into multiple languages.
* **`evaluate_response()`:** Rates responses on keywords.

## Data Storage

*   **User Data (`user_data.json`):** Stores usernames and hashed passwords.
*   **Discussion Data (`discussion_data.db`):**  An SQLite database that stores conversation topics, agent selections, chat histories, summaries, and user associations. *Important:*  For Streamlit Cloud deployments, use an *external* database for persistent storage.
*   **Rating Data (`rating_data.json`):** Stores upvote/downvote counts for agent responses.
*   **Agent Configuration (`agent_config.json`):** Defines the available AI agents.

## Troubleshooting

*   **`ImportError: cannot import name 'genai' from 'google'`:**  Make sure you are importing the Gemini library correctly: `import google.generativeai as genai`.  Ensure that `google-generativeai` is listed in your `requirements.txt` file.
*   **`ValueError: ... is not in iterable` (with `st.radio`):**  Ensure you are passing a *list* of options to the `options` parameter of `st.radio`, not a single string.  Use `format_func` to control the displayed labels.  Use `index` to set the default selection correctly.
*   **"Fehlender Schlüssel: ..." (Missing Key):** This indicates that a text string used in the UI is not present in the `translations` dictionary for the selected language.  Add the missing key-value pair to the appropriate language sub-dictionary within `translations`.
*   **API Errors:**
    *   **Missing API Key:** Ensure you have provided your Gemini API key correctly (using Streamlit Secrets in Streamlit Cloud).
    *   **Rate Limits:** If you encounter `429` errors, you may be exceeding the API rate limits.  Reduce the frequency of API calls (increase `API_SLEEP_SECONDS`) or request a higher quota.
    *   **Invalid Model Name:**  Use a valid and supported model name for `MODEL_NAME_TEXT` and `MODEL_NAME_VISION`.
*   **Connection Errors:**  Check your internet connection.  Long conversations may be more susceptible to connection interruptions.
*   **File Upload/Processing Errors:** Ensure that uploaded files are of the correct type (PDF or image) and are not corrupted.
*   **Database Errors (Local SQLite):** Ensure that the application has the necessary permissions to read and write to the database file.
* **Database Error (Streamlit Cloud):**
   *    Use an external database.
   *    Check your connection string and credentials
*   **"PDF-Datei hochgeladen (Vorschau nicht unterstützt)":**  This is *not* an error; it's an informational message.  Streamlit's `st.file_uploader` doesn't provide built-in PDF previews.

## Contributing

Contributions are welcome!  Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes, ensuring that you follow the existing code style and add appropriate comments.
4.  Add or update tests as needed.
5.  Submit a pull request with a clear description of your changes and their benefits.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This software is provided "as is" without warranty of any kind.  The authors are not responsible for any damages arising from the use of this software.  Use of the Google Gemini API is subject to Google's Terms of Service.

---


### Agenten-Konfiguration (`agent_config.json`)

Die Datei `agent_config.json` definiert die verfügbaren KI-Agenten. Es handelt sich um ein JSON-Array von Objekten, wobei jedes Objekt einen Agenten repräsentiert und *zwingend* die folgenden Eigenschaften haben *muss*:

*   `name`: (String) Der Name des Agenten.
*   `personality`: (String) Die Persönlichkeit des Agenten. Muss einer der folgenden Werte sein: "kritisch", "visionär", "konservativ", "neutral".
*   `description`: (String) Eine kurze Beschreibung des Agenten.

Beispiel:

```json
[
    {
        "name": "AgentA",
        "personality": "kritisch",
        "description": "Ein kritischer Denker, der Argumente hinterfragt."
    },
    {
        "name": "AgentB",
        "personality": "visionär",
        "description": "Ein Visionär, der neue Ideen und Perspektiven einbringt."
    }
]
```

### Übersetzungen (Mehrsprachige Unterstützung)

Das `translations`-Dictionary in Ihrer Haupt-Python-Datei (`streamlit_app.py`) speichert den in der Benutzeroberfläche verwendeten Text in mehreren Sprachen. Jede Sprache hat ein Unter-Dictionary mit Schlüssel-Wert-Paaren. Die *Schlüssel* sind Bezeichner (z.B. `title`, `login_btn`), und die *Werte* sind die übersetzten Zeichenketten.

*   **Hinzufügen einer neuen Sprache:** Fügen Sie dem `translations`-Dictionary ein neues Unter-Dictionary mit dem entsprechenden Sprachcode hinzu (z.B. "fr" für Französisch). Übersetzen Sie *alle* vorhandenen Schlüssel in die neue Sprache.
*   **Hinzufügen von neuem UI-Text:** Wenn Sie neuen Text zur Benutzeroberfläche hinzufügen, fügen Sie einen entsprechenden Eintrag zum `translations`-Dictionary für *alle* unterstützten Sprachen hinzu. Verwenden Sie die Funktion `get_translation(lang, key)`, um den korrekten Text basierend auf der vom Benutzer ausgewählten Sprache abzurufen.

### Konstanten

Mehrere Konstanten in Ihrer Haupt-Python-Datei (`streamlit_app.py`) steuern das Verhalten der Anwendung:

*   `MODEL_NAME_TEXT`: Der Name des Gemini-Modells, das für die Textgenerierung verwendet werden soll (z.B. `"gemini-1.5-pro-002"`).  **Verwenden Sie einen aktuellen, unterstützten Modellnamen.**
*   `MODEL_NAME_VISION`: Der Name des Gemini-Modells, das für die Bildverarbeitung verwendet werden soll (z.B. `"gemini-1.5-pro-002"`). **Verwenden Sie einen aktuellen, unterstützten *Vision*-Modellnamen.**
*   `API_SLEEP_SECONDS`: Die Verzögerung (in Sekunden) zwischen API-Aufrufen, um Ratenbegrenzungen zu vermeiden.
*   `API_MAX_RETRIES`: Die maximale Anzahl von Wiederholungsversuchen für einen API-Aufruf, wenn er fehlschlägt.
*   `SUMMARY_SLEEP_SECONDS`: Eine Verzögerung nach dem Generieren von Zusammenfassungen.
*   `USE_CHAT_HISTORY_FILE`: Setzen Sie dies auf `True`, um den Chatverlauf in eine lokale Datei `chat_history.txt` zu schreiben. Setzen Sie dies auf `False`, um dies zu deaktivieren (empfohlen für Streamlit Cloud-Bereitstellungen).
*   `AUDIT_LOG_FILE`, `EXPIRATION_TIME_SECONDS`, `ROLE_PERMISSIONS`, `PRIORITY_MAP`, `USER_DATA_FILE`, `DISCUSSION_DB_FILE`, `RATING_DATA_FILE`, `AGENT_CONFIG_FILE`: Diese Konstanten definieren Dateinamen, Zeitdauern, Rollenberechtigungen und andere Konfigurationseinstellungen. Ändern Sie diese nur, wenn Sie ihren Zweck verstehen.

## Verwendung

1.  **Sprache auswählen:** Wählen Sie Ihre bevorzugte Sprache aus der Dropdown-Liste in der Seitenleiste.
2.  **Anmelden/Registrieren (Optional):** Erstellen Sie ein neues Konto oder melden Sie sich bei einem bestehenden Konto an, um Ihre Konversationen zu speichern und zu laden.
3.  **Agenten auswählen:** Wählen Sie die KI-Agenten aus, die an der Konversation teilnehmen sollen.
4.  **Eingabe bereitstellen:**
    *   **Thema (Text):** Geben Sie ein Diskussionsthema in das Texteingabefeld ein.
    *   **Datei hochladen (Optional):** Laden Sie ein PDF-Dokument oder ein Bild (PNG, JPG, JPEG, GIF) hoch, um Kontext für die Diskussion bereitzustellen.
5.  **Parameter konfigurieren:** Legen Sie die Anzahl der Konversationsrunden fest.
6.  **Konversation starten:** Klicken Sie auf die Schaltfläche "Konversation starten".
7.  **Interagieren und Bewerten:** Beobachten Sie den Verlauf der Konversation in der Chat-Oberfläche. Sie können einzelne Agentenantworten positiv oder negativ bewerten.
8.  **Speichern/Exportieren:**
    *   **Speichern:** Speichern Sie die Konversation in der Datenbank (erfordert Anmeldung).
    *   **Exportieren:** Laden Sie die Konversation als formatiertes Word-Dokument herunter.

## Bereitstellung auf Streamlit Cloud

1.  **Geheimnisverwaltung:** **Speichern Sie Ihren API-Schlüssel niemals direkt in Ihrem Code.** Verwenden Sie die Geheimnisverwaltung von Streamlit Cloud:
    *   Gehen Sie in Ihrem Streamlit Cloud-Dashboard zu Ihrer App.
    *   Klicken Sie auf das Menü "..." und wählen Sie "Edit Secrets".
    *   Fügen Sie ein Geheimnis mit dem Namen `GEMINI_API_KEY` hinzu und fügen Sie Ihren API-Schlüssel als Wert ein.
    *   Greifen Sie in Ihrem Code mit folgendem Code auf den Schlüssel zu:
        ```python
        api_key = st.secrets["GEMINI_API_KEY"]
        if not api_key:
            st.warning(get_translation(lang, "api_key_warning"))
            st.stop()  # Oder return, wie im bereitgestellten Code
        ```

2.  **Persistenz:** Streamlit Cloud verwendet ein *temporäres* Dateisystem. Dateien, die während der Ausführung der Anwendung geschrieben werden (einschließlich der SQLite-Datenbank), bleiben *nicht* zwischen Neustarts erhalten.
    *   **Für kurzfristige Sitzungsdaten:** Verwenden Sie `st.session_state`.
    *   **Für langfristige Persistenz:** Verwenden Sie einen *externen* Datenbankdienst (PostgreSQL, MySQL, MongoDB Atlas, Firebase, Supabase usw.). Dies erfordert eine Änderung Ihres Codes, um eine Verbindung zur externen Datenbank herzustellen.  *Dies wird dringend für jede Produktionsbereitstellung empfohlen.*
    *   **Deaktivieren Sie `USE_CHAT_HISTORY_FILE`:** Setzen Sie es auf `False`.

## Architektur

Die Anwendung besteht aus den folgenden Hauptkomponenten:

*   **`streamlit_app.py` (oder Ihre Hauptdatei):** Enthält die Streamlit-Benutzeroberfläche, die Ereignisbehandlung und die gesamte Anwendungslogik.
*   **`joint_conversation_with_selected_agents()`:** Die Kernfunktion, die den Konversationsfluss verwaltet, mit der Gemini-API interagiert und Aktualisierungen an die Benutzeroberfläche liefert.
*   **`call_gemini_api()`:** Behandelt die Kommunikation mit der Gemini-API, einschließlich Wiederholungsversuchen und Fehlerbehandlung.
*   **`generate_pdf_summary_from_bytes()`:** Generiert eine Textzusammenfassung aus einer PDF-Datei.
*   **`generate_image_summary_from_bytes()`:** Generiert eine Beschreibung eines Bildes.
*   **`process_uploaded_file()`:** Eine Hilfsfunktion zur Behandlung von PDF- und Bilduploads.
*   **`generate_summary()`:** Generiert eine kurze Zusammenfassung eines gegebenen Textes.
*   **`save_chat_as_word()`:** Exportiert den Konversationsverlauf in ein Word-Dokument.
*   **`load_json_data()`, `save_json_data()`:** Funktionen zum Laden und Speichern von Daten in JSON-Dateien.
*   **`load_user_data()`, `save_user_data()`, `load_rating_data()`, `save_rating_data()`, `load_agent_config()`:** Hilfsfunktionen zum Laden und Speichern bestimmter Datendateien.
*   **`hash_password()`, `verify_password()`:** Funktionen zur sicheren Handhabung von Benutzerpasswörtern.
*   **`register_user()`, `login_user()`:** Funktionen für die Benutzerregistrierung und -anmeldung.
*   **`create_discussion_table()`, `save_discussion_data_db()`, `load_discussion_data_db()`:** Funktionen für die Interaktion mit der SQLite-Datenbank.
*   **`rate_agent_response()`:** Behandelt Benutzerbewertungen von Agentenantworten.
*   **`get_translation()`:** Ruft die entsprechende Übersetzung basierend auf der ausgewählten Sprache ab.
*   **`translations` (Dictionary):** Enthält den gesamten in der Benutzeroberfläche verwendeten Text, übersetzt in mehrere Sprachen.
*   **`evaluate_response()`:** Bewertet Antworten anhand von Schlüsselwörtern.

## Datenspeicherung

*   **Benutzerdaten (`user_data.json`):** Speichert Benutzernamen und gehashte Passwörter.
*   **Diskussionsdaten (`discussion_data.db`):** Eine SQLite-Datenbank, die Konversationsthemen, Agentenauswahlen, Chatverläufe, Zusammenfassungen und Benutzerzuordnungen speichert. *Wichtig:* Verwenden Sie für Streamlit Cloud-Bereitstellungen eine *externe* Datenbank für persistente Speicherung.
*   **Bewertungsdaten (`rating_data.json`):** Speichert die Anzahl der positiven/negativen Bewertungen für Agentenantworten.
*   **Agentenkonfiguration (`agent_config.json`):** Definiert die verfügbaren KI-Agenten.

## Fehlerbehebung

*   **`ImportError: cannot import name 'genai' from 'google'`:** Stellen Sie sicher, dass Sie die Gemini-Bibliothek korrekt importieren: `import google.generativeai as genai`. Stellen Sie sicher, dass `google-generativeai` in Ihrer Datei `requirements.txt` aufgeführt ist.
*   **`ValueError: ... is not in iterable` (mit `st.radio`):** Stellen Sie sicher, dass Sie eine *Liste* von Optionen an den Parameter `options` von `st.radio` übergeben, nicht eine einzelne Zeichenkette. Verwenden Sie `format_func`, um die angezeigten Beschriftungen zu steuern. Verwenden Sie `index`, um die Standardauswahl korrekt festzulegen.
*   **"Fehlender Schlüssel: ...":** Dies zeigt an, dass eine in der Benutzeroberfläche verwendete Textzeichenfolge nicht im `translations`-Dictionary für die ausgewählte Sprache vorhanden ist. Fügen Sie das fehlende Schlüssel-Wert-Paar dem entsprechenden Sprach-Unter-Dictionary innerhalb von `translations` hinzu.
*   **API-Fehler:**
    *   **Fehlender API-Schlüssel:** Stellen Sie sicher, dass Sie Ihren Gemini-API-Schlüssel korrekt angegeben haben (mit Streamlit Secrets in Streamlit Cloud).
    *   **Ratenbegrenzungen:** Wenn Sie `429`-Fehler erhalten, überschreiten Sie möglicherweise die API-Ratenbegrenzungen. Reduzieren Sie die Häufigkeit von API-Aufrufen (erhöhen Sie `API_SLEEP_SECONDS`) oder fordern Sie ein höheres Kontingent an.
    *   **Ungültiger Modellname:** Verwenden Sie einen gültigen und unterstützten Modellnamen für `MODEL_NAME_TEXT` und `MODEL_NAME_VISION`.
*   **Verbindungsfehler:** Überprüfen Sie Ihre Internetverbindung. Lange Konversationen können anfälliger für Verbindungsunterbrechungen sein.
*   **Fehler beim Hochladen/Verarbeiten von Dateien:** Stellen Sie sicher, dass hochgeladene Dateien vom richtigen Typ (PDF oder Bild) und nicht beschädigt sind.
*   **Datenbankfehler (Lokale SQLite):** Stellen Sie sicher, dass die Anwendung über die erforderlichen Berechtigungen zum Lesen und Schreiben in die Datenbankdatei verfügt.
* **Datenbankfehler (Streamlit Cloud):**
   *    Verwenden Sie eine externe Datenbank.
   *    Überprüfen Sie Ihre Verbindungszeichenfolge und Ihre Anmeldeinformationen.
*   **"PDF-Datei hochgeladen (Vorschau nicht unterstützt)":** Dies ist *kein* Fehler, sondern eine Informationsmeldung. Der `st.file_uploader` von Streamlit bietet keine integrierte PDF-Vorschau.

## Mitwirken

Beiträge sind willkommen! Bitte befolgen Sie diese Schritte:

1.  Forken Sie das Repository.
2.  Erstellen Sie einen neuen Branch für Ihr Feature oder Ihren Bugfix.
3.  Implementieren Sie Ihre Änderungen und stellen Sie sicher, dass Sie den vorhandenen Codestil einhalten und entsprechende Kommentare hinzufügen.
4.  Fügen Sie bei Bedarf Tests hinzu oder aktualisieren Sie sie.
5.  Reichen Sie einen Pull Request mit einer klaren Beschreibung Ihrer Änderungen und ihrer Vorteile ein.

## Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

## Haftungsausschluss

Diese Software wird "wie besehen" ohne jegliche Gewährleistung zur Verfügung gestellt. Die Autoren sind nicht verantwortlich für Schäden, die durch die Verwendung dieser Software entstehen. Die Nutzung der Google Gemini API unterliegt den Nutzungsbedingungen von Google.
