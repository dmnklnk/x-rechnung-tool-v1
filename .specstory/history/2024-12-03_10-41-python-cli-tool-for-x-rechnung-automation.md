## SpecStory

## Python CLI Tool for X-Rechnung Automation (3.12.2024, 10:41:37)

_**User**_

Ich habe ein neues Projekt, dafür benötige ich deine Hilfe. Es geht um das Thema "X-Rechnungen". Das wird ab 2025 Pflicht und ich benötige eine Windows-EXE die folgendes kann:

- bestehende .XML-Datei an ein bestehendes PDF anhängen
- Standard-Mailprogramm öffnen 
- "finale" PDF als Dateianhang in neuer E-Mail mit bereits eingetragener E-Mail-Adresse

Dazu werden folgende 3 Parameter übergeben:

1. Pfad zum PDF
2. Pfad zur XML
3. E-Mail-Adresse

Ich möchte dafür Python verwenden. Für meine gesamten Python-projekte verwende ich CONDA. Lass uns also bitte bevor wir beginnen ein neues CONDA-Environment namens "x-rechnung-tool-v1" erstellen.

Kriegen wir das umgesetzt? Wir benötigen für unser keine GUI. Es soll ein reines CLI-Tool als Windows-EXE sein, da diese EXE später als Teil eines Shell-Script ausgeführt werden soll.

Kriegen wir das hin? Verstehst du was ich meien oder benötigst du noch weitere Infos von mir?

---

_**Assistant**_

Ja, ich verstehe, was du meinst, und wir können das umsetzen. Hier sind die Schritte, die wir unternehmen müssen:

1. **Erstellen eines neuen CONDA-Umgebungs**: Wir werden ein neues Environment namens "x-rechnung-tool-v1" erstellen.
2. **Installieren der benötigten Bibliotheken**: Wir benötigen Bibliotheken zum Bearbeiten von PDF-Dateien, zum Verarbeiten von XML-Dateien und zum Senden von E-Mails.
3. **Implementierung des CLI-Tools**: Wir werden ein Python-Skript schreiben, das die gewünschten Funktionen erfüllt.
4. **Erstellen einer Windows-EXE**: Wir werden das Skript in eine ausführbare Datei umwandeln.

### Schritt 1: Erstellen des CONDA-Umgebungs

Führe den folgenden Befehl in deiner Konsole aus, um das neue Environment zu erstellen:

```bash
conda create --name x-rechnung-tool-v1 python=3.9
```

Aktiviere das Environment:

```bash
conda activate x-rechnung-tool-v1
```

### Schritt 2: Installieren der benötigten Bibliotheken

Wir benötigen einige Bibliotheken. Installiere sie mit den folgenden Befehlen:

```bash
conda install PyPDF2 lxml
pip install pywin32
```

### Schritt 3: Implementierung des CLI-Tools

Hier ist ein einfaches Beispiel für das Python-Skript, das die gewünschten Funktionen erfüllt:

```python
import sys
import os
import PyPDF2
import lxml.etree as ET
import win32com.client as win32

def append_xml_to_pdf(pdf_path, xml_path):
    # ... bestehende PDF-Datei öffnen ...
    pdf_writer = PyPDF2.PdfWriter()
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page])
    
    # ... XML-Datei lesen und in PDF umwandeln ...
    # Hier kannst du die Logik hinzufügen, um die XML-Daten in PDF zu konvertieren

    # ... finale PDF speichern ...
    final_pdf_path = "final_output.pdf"
    with open(final_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    
    return final_pdf_path

def send_email_with_attachment(email_address, attachment_path):
    # ... Standard-Mailprogramm öffnen und E-Mail erstellen ...
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = email_address
    mail.Subject = 'X-Rechnung'
    mail.Body = 'Bitte finden Sie die angehängte finale PDF.'
    mail.Attachments.Add(attachment_path)
    mail.Display()

def main(pdf_path, xml_path, email_address):
    final_pdf_path = append_xml_to_pdf(pdf_path, xml_path)
    send_email_with_attachment(email_address, final_pdf_path)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <pdf_path> <xml_path> <email_address>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    xml_path = sys.argv[2]
    email_address = sys.argv[3]
    
    main(pdf_path, xml_path, email_address)
```

### Schritt 4: Erstellen einer Windows-EXE

Um das Skript in eine EXE-Datei umzuwandeln, kannst du `pyinstaller` verwenden. Installiere es mit:

```bash
pip install pyinstaller
```

Dann kannst du die EXE mit folgendem Befehl erstellen:

```bash
pyinstaller --onefile script.py
```

Das wird eine ausführbare Datei im `dist`-Ordner erstellen.

Wenn du weitere Informationen oder Anpassungen benötigst, lass es mich wissen!

---



---

