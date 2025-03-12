# CipherCore Agent Conversation Platform

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-brightgreen)](https://ai-think-tank-5vtskdnb8xtgvonz4qqgvm.streamlit.app)

A powerful Streamlit application that simulates conversations between AI agents, allowing users to explore different perspectives on various topics.  Powered by the Gemini AI model, this platform facilitates dynamic discussions and provides a unique environment for brainstorming, analysis, and creative exploration.

[**Live Demo: CipherCore Agent Conversation Platform**](https://ai-think-tank-5vtskdnb8xtgvonz4qqgvm.streamlit.app)

## Key Features

*   **Dynamic AI Agent Selection:** Choose from a variety of pre-configured AI agents, each with a unique personality (critical, visionary, conservative, neutral) and area of expertise. The agent configurations are dynamically loaded from `agent_config.json`, allowing for easy customization and extension.
*   **Interactive Conversation Simulation:** Define the discussion topic, set the number of conversation rounds, and initiate a collaborative exchange between the selected agents.
*   **User Authentication:** Secure user accounts with login and registration features, enabling users to save and load their discussions.
*   **Discussion History:** Save and load conversation histories to SQLite database, allowing for easy review and continuation of previous sessions.
*   **Response Evaluation:** Rate agent responses with upvotes and downvotes to provide feedback on their performance.
*   **Word Export:** Download the complete conversation history as a formatted Word document (.docx) for easy sharing and archival.
*   **Multi-Language Support:** Agents can converse in Deutsch, English, French, or Spanish, allowing for global collaboration.
*   **API Key Security:** API key is securely managed by the user via the web-ui, instead of using environment variables.

## Table of Contents

*   [Introduction](#introduction)
*   [Features](#key-features)
*   [Architecture](#architecture)
*   [Configuration](#configuration)
*   [Usage](#usage)
*   [Data Storage](#data-storage)
*   [Contributing](#contributing)
*   [License](#license)

## Introduction

The CipherCore Agent Conversation Platform is designed to showcase the power of AI collaboration. Users can customize their experience by selecting different agents with various personalities and areas of expertise to create dynamic and insightful discussions on a wide range of topics.  This project leverages the Streamlit framework for a user-friendly interface and the Gemini AI model for intelligent agent responses.

## Architecture

The application follows a modular architecture, comprising the following key components:

*   **User Interface (Streamlit):** Handles user interaction, agent selection, topic input, and display of conversation history.
*   **AI Agent Logic:**  Manages the prompts sent to the Gemini AI model and processes agent responses.
*   **Data Management:**  Handles user authentication, session management, and storage of discussion data using JSON files and SQLite.
*   **Gemini API Integration:**  Communicates with the Gemini AI model to generate agent responses.
*   **Word Export:**  The python-docx library allows downloading converstations into a report

## Configuration

1.  **Gemini API Key:**  Obtain a Gemini API key from Google AI Studio and enter it in the designated sidebar field in the Streamlit application.
2.  **Agent Configuration (`agent_config.json`):** This file defines the available AI agents, their personalities, and descriptions.  The structure follows the `AGENT_CONFIG_SCHEMA` in the code.
3.  **User Data (`user_data.json`):**  Stores user credentials (usernames and hashed passwords).  The structure follows the `USER_DATA_SCHEMA` in the code.
4.  **Other Data Files:** The Application creates three key files for proper functionality.
* agent_config.json: The key file configures the agent for use in the application
* rating_data.json: Tracks all upvotes and downvotes for discussion_id
* discussion_data.db: Tracks all Discussions for logged in users.

**Example `agent_config.json`:**

```json
[
  {
    "name": "Marketingexperte",
    "personality": "visionär",
    "description": "Spezialist für innovative Marketingstrategien und Markttrends."
  },
  {
    "name": "Softwareentwickler",
    "personality": "kritisch",
    "description": "Experte für Softwarearchitektur, Codequalität und Sicherheitsaspekte."
  }
]
```

## Usage

1.  **Launch the Streamlit app:** Open the `streamlit_app.py` file in your editor and run it.
2.  **Enter API Key:** Enter your Gemini API key in the sidebar.
3.  **Login/Register:** Create a new account or login with an existing one.
4.  **Select Agents:** Choose the AI agents you want to participate in the conversation from the expandable agent selection menu.
5.  **Configure Conversation:** Enter the discussion topic, select the number of rounds, expertise level, and language.
6.  **Start Conversation:**  Click the "Konversation starten" button to initiate the simulation.
7.  **Review and Rate:** Review the agent responses and provide feedback using the upvote and downvote buttons.
8.  **Save or Export:** Save the discussion to the database or download it as a Word document.

## Data Storage

*   **User Data:**  Usernames and hashed passwords are stored in `user_data.json`.
*   **Discussion Data:** Conversation topics, agent names, chat histories, summaries, and user information are stored in the SQLite database `discussion_data.db`.
*   **Rating Data:** Upvote and downvote counts for agent responses are stored in `rating_data.json`.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes.
4.  Submit a pull request with a clear description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).




# CipherCore Agenten-Konversationsplattform

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-brightgreen)](https://ai-think-tank-5vtskdnb8xtgvonz4qqgvm.streamlit.app)

Eine leistungsstarke Streamlit-Anwendung, die Konversationen zwischen KI-Agenten simuliert und es Benutzern ermöglicht, verschiedene Perspektiven zu unterschiedlichen Themen zu erkunden.  Angetrieben vom Gemini AI-Modell, erleichtert diese Plattform dynamische Diskussionen und bietet eine einzigartige Umgebung für Brainstorming, Analyse und kreative Erkundung.

[**Live-Demo: CipherCore Agenten-Konversationsplattform**](https://ai-think-tank-5vtskdnb8xtgvonz4qqgvm.streamlit.app)

## Hauptmerkmale

*   **Dynamische KI-Agenten-Auswahl:** Wählen Sie aus einer Vielzahl vorkonfigurierter KI-Agenten, jeder mit einer einzigartigen Persönlichkeit (kritisch, visionär, konservativ, neutral) und einem Fachgebiet. Die Agentenkonfigurationen werden dynamisch aus `agent_config.json` geladen, was eine einfache Anpassung und Erweiterung ermöglicht.
*   **Interaktive Konversationssimulation:** Definieren Sie das Diskussionsthema, legen Sie die Anzahl der Gesprächsrunden fest und initiieren Sie einen kollaborativen Austausch zwischen den ausgewählten Agenten.
*   **Benutzerauthentifizierung:** Sichere Benutzerkonten mit Anmelde- und Registrierungsfunktionen, die es Benutzern ermöglichen, ihre Diskussionen zu speichern und zu laden.
*   **Diskussionsverlauf:** Speichern und laden Sie Konversationsverläufe in einer SQLite-Datenbank, um frühere Sitzungen einfach zu überprüfen und fortzusetzen.
*   **Antwortbewertung:** Bewerten Sie Agentenantworten mit "Daumen hoch" und "Daumen runter", um Feedback zu ihrer Leistung zu geben.
*   **Word-Export:** Laden Sie den vollständigen Konversationsverlauf als formatierte Word-Datei (.docx) herunter, um ihn einfach weiterzugeben und zu archivieren.
*   **Mehrsprachige Unterstützung:** Agenten können auf Deutsch, Englisch, Französisch oder Spanisch konversieren, was eine globale Zusammenarbeit ermöglicht.
*   **API-Schlüssel Sicherheit:** Der API-Schlüssel wird vom Benutzer sicher über die Weboberfläche verwaltet, anstatt Umgebungsvariablen zu verwenden.

## Inhaltsverzeichnis

*   [Einleitung](#einleitung)
*   [Hauptmerkmale](#hauptmerkmale)
*   [Architektur](#architektur)
*   [Konfiguration](#konfiguration)
*   [Verwendung](#verwendung)
*   [Datenspeicherung](#datenspeicherung)
*   [Beitragen](#beitragen)
*   [Lizenz](#lizenz)

## Einleitung

Die CipherCore Agenten-Konversationsplattform soll die Leistungsfähigkeit der KI-Zusammenarbeit demonstrieren. Benutzer können ihre Erfahrung anpassen, indem sie verschiedene Agenten mit unterschiedlichen Persönlichkeiten und Fachgebieten auswählen, um dynamische und aufschlussreiche Diskussionen zu einer Vielzahl von Themen zu erstellen.  Dieses Projekt nutzt das Streamlit-Framework für eine benutzerfreundliche Oberfläche und das Gemini AI-Modell für intelligente Agentenantworten.

## Architektur

Die Anwendung folgt einer modularen Architektur, die die folgenden Schlüsselkomponenten umfasst:

*   **Benutzeroberfläche (Streamlit):** Verarbeitet die Benutzerinteraktion, Agentenauswahl, Themeneingabe und Anzeige des Konversationsverlaufs.
*   **KI-Agentenlogik:** Verwaltet die an das Gemini AI-Modell gesendeten Prompts und verarbeitet Agentenantworten.
*   **Datenverwaltung:** Verwaltet die Benutzerauthentifizierung, Sitzungsverwaltung und Speicherung von Diskussionsdaten mithilfe von JSON-Dateien und SQLite.
*   **Gemini API-Integration:** Kommuniziert mit dem Gemini AI-Modell, um Agentenantworten zu generieren.
*   **Word-Export:** Die python-docx-Bibliothek ermöglicht das Herunterladen von Gesprächen in einen Bericht.

## Konfiguration

1.  **Gemini API-Schlüssel:**  Besorgen Sie sich einen Gemini API-Schlüssel von Google AI Studio und geben Sie ihn in das dafür vorgesehene Seitenleistenfeld in der Streamlit-Anwendung ein.
2.  **Agentenkonfiguration (`agent_config.json`):** Diese Datei definiert die verfügbaren KI-Agenten, ihre Persönlichkeiten und Beschreibungen.  Die Struktur folgt dem `AGENT_CONFIG_SCHEMA` im Code.
3.  **Benutzerdaten (`user_data.json`):** Speichert Benutzeranmeldeinformationen (Benutzernamen und gehashte Passwörter).  Die Struktur folgt dem `USER_DATA_SCHEMA` im Code.
4.  **Andere Datendateien:** Die Anwendung erstellt drei wichtige Dateien für die ordnungsgemäße Funktion:
    * agent\_config.json: Die Schlüsseldatei konfiguriert den Agenten zur Verwendung in der Anwendung.
    * rating\_data.json: Verfolgt alle Upvotes und Downvotes für discussion\_id.
    * discussion\_data.db: Verfolgt alle Diskussionen für angemeldete Benutzer.

**Beispiel `agent_config.json`:**

```json
[
  {
    "name": "Marketingexperte",
    "personality": "visionär",
    "description": "Spezialist für innovative Marketingstrategien und Markttrends."
  },
  {
    "name": "Softwareentwickler",
    "personality": "kritisch",
    "description": "Experte für Softwarearchitektur, Codequalität und Sicherheitsaspekte."
  }
]
```

## Verwendung

1.  **Starten Sie die Streamlit-App:** Öffnen Sie die Datei `streamlit_app.py` in Ihrem Editor und führen Sie sie aus.
2.  **Geben Sie den API-Schlüssel ein:** Geben Sie Ihren Gemini API-Schlüssel in der Seitenleiste ein.
3.  **Anmelden/Registrieren:** Erstellen Sie ein neues Konto oder melden Sie sich mit einem bestehenden Konto an.
4.  **Agenten auswählen:** Wählen Sie die KI-Agenten aus, die an der Konversation teilnehmen sollen, über das aufklappbare Agentenauswahlmenü.
5.  **Konversation konfigurieren:** Geben Sie das Diskussionsthema ein, wählen Sie die Anzahl der Gesprächsrunden, das Expertenniveau und die Sprache aus.
6.  **Konversation starten:**  Klicken Sie auf die Schaltfläche "Konversation starten", um die Simulation zu initiieren.
7.  **Überprüfen und Bewerten:** Überprüfen Sie die Agentenantworten und geben Sie Feedback mithilfe der "Daumen hoch"- und "Daumen runter"-Schaltflächen.
8.  **Speichern oder Exportieren:** Speichern Sie die Diskussion in der Datenbank oder laden Sie sie als Word-Dokument herunter.

## Datenspeicherung

*   **Benutzerdaten:**  Benutzernamen und gehashte Passwörter werden in `user_data.json` gespeichert.
*   **Diskussionsdaten:** Konversationsthemen, Agentennamen, Chatprotokolle, Zusammenfassungen und Benutzerinformationen werden in der SQLite-Datenbank `discussion_data.db` gespeichert.
*   **Bewertungsdaten:** Upvote- und Downvote-Zahlen für Agentenantworten werden in `rating_data.json` gespeichert.

## Beitragen

Beiträge sind willkommen! Bitte folgen Sie diesen Schritten:

1.  Forken Sie das Repository.
2.  Erstellen Sie einen neuen Branch für Ihr Feature oder Ihren Bugfix.
3.  Implementieren Sie Ihre Änderungen.
4.  Senden Sie einen Pull Request mit einer klaren Beschreibung Ihrer Änderungen.

## Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.


