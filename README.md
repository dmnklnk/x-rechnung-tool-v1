# X-Rechnung Tool

Ein Command-Line-Tool zum Anhängen von X-Rechnung XML-Dateien an PDFs und automatischer E-Mail-Erstellung.

## Funktionen

- Fügt eine X-Rechnung (XML) als Anhang zu einer bestehenden PDF-Datei hinzu
- Erstellt automatisch eine Backup-Kopie der Original-PDF
- Öffnet eine neue E-Mail im Standard-Mail-Client (Outlook) mit:
  - Vordefinierter Empfänger-Adresse
  - Automatisch angehängter PDF (inkl. eingebetteter XML)

## Verwendung

```bash
x_rechnung_tool.exe "C:\pfad\zur\rechnung.pdf" "C:\pfad\zur\rechnung.xml" "empfaenger@firma.de"
```

### Parameter

1. `pdf_path`: Pfad zur PDF-Datei
2. `xml_path`: Pfad zur XML-Datei (X-Rechnung)
3. `email`: E-Mail-Adresse des Empfängers

## Technische Details

- Entwickelt in Python 3.11
- Verwendet PyPDF2 für PDF-Manipulation
- Verwendet pywin32 für Outlook-Integration
- Windows-kompatibel

## Abhängigkeiten

- PyPDF2==3.0.1
- pywin32==306
