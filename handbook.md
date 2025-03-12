# CipherCore Agent Conversation Platform - User Guide

## Introduction

This guide walks you through the user interface of the CipherCore Agent Conversation Platform, explaining the features and usage of each element. This platform allows you to create simulated conversations between different AI agents to gain diverse perspectives on a variety of topics.

## User Interface Overview

The platform's user interface is divided into several sections:

1.  **Title and Description:** At the top of the page, you'll find the title "CipherCore Agent Conversation Platform" along with a brief description of the application's purpose and benefits.
2.  **API Key Input:** The sidebar features the "API Key" field where you must enter your Gemini API key to use the application.
3.  **Login/Registration:** An expandable section where you can log in or create a new account.
4.  **Agent Selection:** An expandable section where you can select the participating AI agents and their personalities.
5.  **Conversation Settings:** This section allows you to define the discussion topic, number of conversation rounds, expertise level, and language.
6.  **Saved Discussions:** An expandable section where you can load and view previously saved discussions.
7.  **Agent Conversation (Chatbot):** The main area where the simulated conversation between the agents is displayed.
8.  **Formatted Output:** An area displaying the conversation in a formatted text format.
9.  **Rating Section:** A section where you can rate the agents' responses.
10. **Buttons:** Buttons to start the conversation, save the discussion, and export the chat as a Word file.

## Detailed Usage Instructions

### 1. API Key Input

1.  **Obtain Gemini API Key:** To bring the AI agents to life, you'll need a valid API key from Google Gemini AI Studio. Visit [Google AI Studio](https://makersuite.google.com/) and create or log in to your account. Create a new API Key for the Gemini Model.
2.  **Locate the API Key Field:** In the sidebar panel, find the field labeled "API Key". Click inside the text box.
3.  **Paste API Key:** Paste your Gemini API key into the text field. Make sure the key is correct and doesn't contain any extra spaces.
4.  **Application Hint:** If no API key is entered, you will be notified by a warning message. Without a valid API Key, the application will not function, and conversation will not start.

### 2. Login/Registration

1.  **Expand Login / Registration:** Click on the expandable "Login / Registration" section to display the login and registration forms.
2.  **Login:**
    *   Enter your username in the "Nutzername" (Username) field.
    *   Enter your password in the "Passwort" (Password) field.
    *   Click the "Login" button.
    *   If the login is successful, a success message will appear, and your username will be displayed at the top right.
    *   If the login fails, an error message will be displayed.
3.  **Register:**
    *   Enter a username in the "Nutzername" (Username) field.
    *   Enter a password in the "Passwort" (Password) field.
    *   The password must be at least 8 characters long.
    *   Click the "Registrieren" (Register) button.
    *   If the registration is successful, a success message will be displayed.
    *   If the registration fails, an error message will be displayed, such as if the username is already taken or the password is too short.

### 3. Agent Selection

1.  **Expand Agent Selection:** Click on the expandable "Agenten Auswahl (auf-/zuklappbar)" (Agent Selection (expandable/collapsible)) section to display the list of available AI agents.
2.  **Select Agents:**
    *   Each agent has a checkbox. Check the box next to an agent's name to select it for the conversation.
    *   You can select any number of agents.
3.  **Set Personality:**
    *   For each selected agent, there is a radio button set for selecting the personality: "kritisch" (critical), "visionär" (visionary), "konservativ" (conservative), or "neutral".
    *   Select the desired personality for each agent.
4.  **View Configurations:** The agent names as well as the chosen personalities will be used for generation of the data.

### 4. Conversation Settings

1.  **Discussion Topic:** In the "Diskussionsthema" (Discussion Topic) field, enter the topic that the agents should discuss.
    *   The topic should be precise and clearly formulated to provide the agents with a clear task.
2.  **Number of Conversation Rounds:** Use the "Anzahl Gesprächsrunden" (Number of Conversation Rounds) slider to set how many rounds the simulation should last.
    *   The default value is 10.
    *   You can set a value between 20 and 100.
    *   The higher the number of conversation rounds, the longer and more detailed the conversation will be.
3.  **Expert Level:** Use the "Experten-Level" (Expert Level) radio buttons to choose the desired expertise of the agents: "Beginner", "Fortgeschritten" (Advanced), or "Experte" (Expert).
    *   The default setting is "Experte" (Expert).
4.  **Language:** Use the "Sprache" (Language) radio buttons to choose the desired language for the conversation: "Deutsch" (German), "Englisch" (English), "Französisch" (French), or "Spanisch" (Spanish).
    *   The default setting is "Deutsch" (German).

### 5. Saved Discussions

1.  **Expand Saved Discussions:** Click on the expandable "Gespeicherte Diskussionen" (Saved Discussions) section to view any saved discussions (if any).
2.  **Load Discussions:** Click the "Diskussionen laden" (Load Discussions) button to retrieve your previously saved discussions from the database.
3.  **List of Discussions:** After loading, a list of your saved discussions will be displayed, including information.

### 6. Start and View Conversation

1.  **Start Conversation:** After making all settings, click the "Konversation starten" (Start Conversation) button.
2.  **Agent Conversation:** The simulated conversation is displayed in the "Agenten-Konversation" (Agent Conversation) section (Chatbot).
    *   Each message is displayed with the name of the agent and the corresponding text.
    *   The conversation will continue over the specified number of conversation rounds.
3.  **Formatted Output:** The formatted output is displayed in more detail and can be made more detailed by clicking.

### 7. Rate Responses

1.  **Rating Section:** After each agent's response, a rating section is displayed.
2.  **Rate:**
    *   Click the "👍" button to rate the response as helpful or relevant (Upvote).
    *   Click the "👎" button to rate the response as unhelpful or irrelevant (Downvote).
    *   The rating is stored in the database and used for future improvements to the system.

### 8. Save Discussion and Export as Word

1.  **Save Discussion:**
    *   Click the "Diskussion speichern" (Save Discussion) button to save the current conversation to the database.
    *   The saved discussion can be loaded and continued later.
2.  **Export as Word:**
    *   Click the "Chat als Word speichern" (Save Chat as Word) button to download the current conversation as a formatted Word file (.docx).
    *   The Word file contains the complete conversation history with the names of the agents and the respective texts.

## Troubleshooting

*   **Invalid API Key:** Make sure your Gemini API key is correct. Verify your API key under [Google AI Studio](https://makersuite.google.com/).
*   **No Agents Selected:** Select at least one agent to start a conversation.
*   **Conversation Doesn't Start:** Check the browser console for error messages. Make sure that all required Python packages are installed correctly (see `requirements.txt`).

## Support and Contact

For questions or problems, please contact the CipherCore support team.
