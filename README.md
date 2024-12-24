# X-Rechnung Tool

Ein Command-Line-Tool zum Anhängen von X-Rechnung XML-Dateien an PDFs und automatischer E-Mail-Erstellung.

## Funktionen

- Fügt eine X-Rechnung (XML) als Anhang zu einer bestehenden PDF-Datei hinzu
- Erstellt automatisch eine Backup-Kopie der Original-PDF
- Drei Betriebsmodi:
  1. Nur PDF erstellen
  2. PDF erstellen und E-Mail öffnen
  3. PDF erstellen und E-Mail automatisch senden

## Verwendung

```bash
x-rechnung-tool.exe "C:\pfad\zur\rechnung.pdf" "C:\pfad\zur\rechnung.xml" "empfaenger@firma.de" mode
```

### Parameter

1. `pdf_path`: Pfad zur PDF-Datei
2. `xml_path`: Pfad zur XML-Datei (X-Rechnung)
3. `email`: E-Mail-Adresse des Empfängers
4. `mode`: Betriebsmodus (1, 2 oder 3)
   - `1`: Nur PDF erstellen
   - `2`: PDF erstellen und E-Mail öffnen
   - `3`: PDF erstellen und E-Mail automatisch senden

### Ausgabe

- Eine neue PDF-Datei mit eingebetteter XML am ursprünglichen Speicherort
- Die Original-PDF wird mit dem Suffix "\_original" gesichert
- Je nach Modus:
  - Modus 1: Nur PDF-Erstellung
  - Modus 2: Neue Outlook-E-Mail wird geöffnet
  - Modus 3: E-Mail wird automatisch versendet
- Der absolute Pfad zur erstellten PDF wird ausgegeben

## Technische Details

- Entwickelt in Python 3.11
- Verwendet pikepdf für robuste PDF-Manipulation
- Verwendet pywin32 für Outlook-Integration
- Windows-kompatibel

## Abhängigkeiten

- pikepdf==8.11.1
- pywin32==306
- chardet==5.2.0

## Build

Das Tool wird automatisch via GitHub Actions als Windows-EXE kompiliert.
Neue Releases werden automatisch erstellt, wenn ein neuer Tag gepusht wird:

```bash
git tag v1.0.0
git push origin v1.0.0
```
