# CipherCore Agenten-Konversationsplattform - Benutzerhandbuch

## Einleitung

Dieses Handbuch führt Sie durch die Benutzeroberfläche der CipherCore Agenten-Konversationsplattform und erklärt die Funktionen und Verwendung jedes Elements. Diese Plattform ermöglicht es Ihnen, simulierte Gespräche zwischen verschiedenen KI-Agenten zu erstellen, um unterschiedliche Perspektiven auf vielfältige Themen zu erhalten.

## Übersicht der Benutzeroberfläche

Die Benutzeroberfläche der Plattform ist in verschiedene Bereiche unterteilt:

1.  **Titel und Beschreibung:** Am oberen Rand der Seite befindet sich der Titel "CipherCore Agenten-Konversationsplattform" sowie eine kurze Beschreibung des Zwecks und der Vorteile der Anwendung.
2.  **API-Schlüssel-Eingabe:** In der Seitenleiste finden Sie das Feld "API-Schlüssel", in das Sie Ihren Gemini API-Schlüssel eingeben müssen, um die Anwendung nutzen zu können.
3.  **Login/Registrierung:** Ein aufklappbarer Bereich, in dem Sie sich anmelden oder ein neues Konto erstellen können.
4.  **Agenten-Auswahl:** Ein aufklappbarer Bereich, in dem Sie die teilnehmenden KI-Agenten und deren Persönlichkeiten auswählen können.
5.  **Konversationseinstellungen:** Hier können Sie das Diskussionsthema, die Anzahl der Gesprächsrunden, das Expertenniveau und die Sprache festlegen.
6.  **Gespeicherte Diskussionen:** Ein aufklappbarer Bereich, in dem Sie gespeicherte Diskussionen laden und ansehen können.
7.  **Agenten-Konversation (Chatbot):** Der Hauptbereich, in dem die simulierte Konversation zwischen den Agenten angezeigt wird.
8.  **Formatierter Output:** Ein Bereich, in dem die Konversation im formatierten Textformat angezeigt wird.
9.  **Bewertungsbereich:** Ein Bereich, in dem Sie die Antworten der Agenten bewerten können.
10. **Schaltflächen:** Schaltflächen zum Starten der Konversation, Speichern der Diskussion und Exportieren des Chats als Word-Datei.

## Detaillierte Bedienungsanleitung

### 1. API-Schlüssel-Eingabe

1.  **Gemini API-Schlüssel:** Um die KI-Agenten zum Leben zu erwecken, benötigen Sie einen gültigen API-Schlüssel vom Google Gemini AI Studio. Besuchen Sie [Google AI Studio](https://makersuite.google.com/) und erstellen Sie ein Konto oder melden Sie sich an. Erstellen Sie einen neuen API-Schlüssel für das Gemini-Modell.
2.  **API-Schlüssel eingeben:** Im Seitenleistenbereich, suchen Sie das Feld mit der Bezeichnung "API-Schlüssel". Klicken Sie in das Textfeld.
3.  **API-Schlüssel einfügen:** Fügen Sie Ihren Gemini API-Schlüssel in das Textfeld ein. Achten Sie darauf, dass der Schlüssel korrekt ist und keine zusätzlichen Leerzeichen enthält.
4.  **Anwendungshinweis:** Wenn kein API-Schlüssel eingegeben wird, werden Sie durch einen Warnhinweis darauf hingewiesen. Ohne gültigen API-Schlüssel können die KI-Agenten nicht antworten und die Konversation kann nicht gestartet werden.

### 2. Login/Registrierung

1.  **Login / Registrierung ausklappen:** Klicken Sie auf den aufklappbaren Bereich "Login / Registrierung", um die Anmelde- und Registrierungsformulare anzuzeigen.
2.  **Anmelden:**
    *   Geben Sie Ihren Benutzernamen in das Feld "Nutzername" ein.
    *   Geben Sie Ihr Passwort in das Feld "Passwort" ein.
    *   Klicken Sie auf die Schaltfläche "Login".
    *   Wenn die Anmeldung erfolgreich ist, wird eine Erfolgsmeldung angezeigt und Ihr Benutzername wird oben rechts angezeigt.
    *   Bei fehlgeschlagener Anmeldung wird eine Fehlermeldung angezeigt.
3.  **Registrieren:**
    *   Geben Sie einen Benutzernamen in das Feld "Nutzername" ein.
    *   Geben Sie ein Passwort in das Feld "Passwort" ein.
    *   Das Passwort muss mindestens 8 Zeichen lang sein.
    *   Klicken Sie auf die Schaltfläche "Registrieren".
    *   Bei erfolgreicher Registrierung wird eine Erfolgsmeldung angezeigt.
    *   Bei fehlgeschlagener Registrierung wird eine Fehlermeldung angezeigt, z. B. wenn der Benutzername bereits vergeben ist oder das Passwort zu kurz ist.

### 3. Agenten-Auswahl

1.  **Agenten-Auswahl ausklappen:** Klicken Sie auf den aufklappbaren Bereich "Agenten-Auswahl (auf-/zuklappbar)", um die Liste der verfügbaren KI-Agenten anzuzeigen.
2.  **Agenten auswählen:**
    *   Jeder Agent hat ein Kontrollkästchen. Aktivieren Sie das Kontrollkästchen neben dem Namen eines Agenten, um ihn für die Konversation auszuwählen.
    *   Sie können beliebig viele Agenten auswählen.
3.  **Persönlichkeit festlegen:**
    *   Für jeden ausgewählten Agenten gibt es ein Radio-Button-Set zur Auswahl der Persönlichkeit: "kritisch", "visionär", "konservativ" oder "neutral".
    *   Wählen Sie die gewünschte Persönlichkeit für jeden Agenten aus.
4.  **Konfigurationen einsehen:** Die Agentennamen sowie die gewählten Persönlichkeiten werden als Auswahl für die Generierung genutzt.

### 4. Konversationseinstellungen

1.  **Diskussionsthema:** Geben Sie in das Feld "Diskussionsthema" das Thema ein, über das die Agenten diskutieren sollen.
    *   Das Thema sollte präzise und klar formuliert sein, um den Agenten eine klare Aufgabenstellung zu geben.
2.  **Anzahl Gesprächsrunden:** Verwenden Sie den Schieberegler "Anzahl Gesprächsrunden", um festzulegen, wie viele Gesprächsrunden die Simulation dauern soll.
    *   Der Standardwert ist 10.
    *   Sie können einen Wert zwischen 20 und 100 einstellen.
    *   Je höher die Anzahl der Gesprächsrunden, desto länger und ausführlicher wird die Konversation.
3.  **Experten-Level:** Wählen Sie über die Radio-Buttons "Experten-Level" das gewünschte Fachwissen der Agenten aus: "Beginner", "Fortgeschritten" oder "Experte".
    *   Die Standardeinstellung ist "Experte".
4.  **Sprache:** Wählen Sie über die Radio-Buttons "Sprache" die gewünschte Sprache für die Konversation aus: "Deutsch", "Englisch", "Französisch" oder "Spanisch".
    *   Die Standardeinstellung ist "Deutsch".

### 5. Gespeicherte Diskussionen

1.  **Gespeicherte Diskussionen ausklappen:** Klicken Sie auf den aufklappbaren Bereich "Gespeicherte Diskussionen", um gespeicherte Diskussionen anzuzeigen (sofern welche vorhanden sind).
2.  **Diskussionen laden:** Klicken Sie auf die Schaltfläche "Diskussionen laden", um Ihre zuvor gespeicherten Diskussionen aus der Datenbank abzurufen.
3.  **Liste der Diskussionen:** Nach dem Laden wird eine Liste Ihrer gespeicherten Diskussionen angezeigt, einschliesslich Thema, Agenten und Keyinformationen

### 6. Konversation starten und anzeigen

1.  **Konversation starten:** Nachdem Sie alle Einstellungen vorgenommen haben, klicken Sie auf die Schaltfläche "Konversation starten".
2.  **Agenten-Konversation:** Die simulierte Konversation wird im Bereich "Agenten-Konversation" (Chatbot) angezeigt.
    *   Jede Nachricht wird mit dem Namen des Agenten und dem jeweiligen Text angezeigt.
    *   Die Konversation wird über die angegebene Anzahl von Gesprächsrunden fortgesetzt.
3.  **Formatierter Output:** Der formatierte Output wird detaillierter dargestellt und kann über `Schaltflächen`, auch zu Word Dokumenten gesichert werden.

### 7. Antworten bewerten

1.  **Bewertungsbereich:** Nach jeder Agentenantwort wird ein Bewertungsbereich angezeigt.
2.  **Bewerten:**
    *   Klicken Sie auf die Schaltfläche "👍", um die Antwort als hilfreich oder relevant zu bewerten (Upvote).
    *   Klicken Sie auf die Schaltfläche "👎", um die Antwort als nicht hilfreich oder irrelevant zu bewerten (Downvote).
    *   Die Bewertung wird in der Datenbank gespeichert und für zukünftige Verbesserungen des Systems verwendet.

### 8. Diskussion speichern und als Word exportieren

1.  **Diskussion speichern:**
    *   Klicken Sie auf die Schaltfläche "Diskussion speichern", um die aktuelle Konversation in der Datenbank zu speichern.
    *   Die gespeicherte Diskussion kann später geladen und fortgesetzt werden.
2.  **Als Word exportieren:**
    *   Klicken Sie auf die Schaltfläche "Chat als Word speichern", um die aktuelle Konversation als formatierte Word-Datei (.docx) herunterzuladen.
    *   Die Word-Datei enthält den vollständigen Konversationsverlauf mit den Namen der Agenten und den jeweiligen Texten.

## Fehlerbehebung

*   **API-Schlüssel ungültig:** Stellen Sie sicher, dass Ihr Gemini API-Schlüssel korrekt ist. Überprüfen Sie Ihren API-Schlüssel unter [Google AI Studio](https://makersuite.google.com/).
*   **Keine Agenten ausgewählt:** Wählen Sie mindestens einen Agenten aus, um eine Konversation zu starten.
*   **Konversation startet nicht:** Überprüfen Sie die Browser-Konsole auf Fehlermeldungen. Stellen Sie sicher, dass alle erforderlichen Python-Pakete korrekt installiert sind (siehe `requirements.txt`).

## Support und Kontakt

Bei Fragen oder Problemen wenden Sie sich bitte an das CipherCore-Supportteam.
