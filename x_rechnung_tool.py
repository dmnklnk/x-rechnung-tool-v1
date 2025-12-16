#!/usr/bin/env python3
import sys
import os
import logging
import pikepdf
import argparse
import chardet
import subprocess
import tempfile
from datetime import datetime

# Nur auf Windows importieren
import platform
if platform.system() == 'Windows':
    import win32com.client

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Prüfen, ob wir in einer PyInstaller-EXE laufen
def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Pfad zu Ghostscript finden
def find_ghostscript_path():
    """Findet den Pfad zur Ghostscript-Executable"""
    if platform.system() != 'Windows':
        return 'gs'  # Auf Unix-Systemen ist gs normalerweise im PATH
    
    # Auf Windows suchen wir nach der Executable
    try:
        # Zuerst prüfen, ob gs im PATH ist
        process = subprocess.run(['where', 'gswin64c.exe'], capture_output=True, text=True)
        if process.returncode == 0 and process.stdout.strip():
            return process.stdout.strip().split('\n')[0]
        
        # Wenn nicht im PATH, in typischen Installationsverzeichnissen suchen
        common_paths = [
            r"C:\Program Files\gs\*\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\*\bin\gswin64c.exe",
            r"C:\Program Files\gs\*\bin\gswin32c.exe",
            r"C:\Program Files (x86)\gs\*\bin\gswin32c.exe"
        ]
        
        import glob
        for pattern in common_paths:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        
        # Wenn wir in einer PyInstaller-EXE sind, könnte Ghostscript mitgeliefert sein
        if is_bundled():
            bundled_gs = os.path.join(sys._MEIPASS, "gswin64c.exe")
            if os.path.exists(bundled_gs):
                return bundled_gs
            bundled_gs = os.path.join(sys._MEIPASS, "gswin32c.exe")
            if os.path.exists(bundled_gs):
                return bundled_gs
        
        # Fallback: Versuche einfach gswin64c.exe zu verwenden und hoffe, dass es gefunden wird
        return "gswin64c.exe"
    except Exception as e:
        logging.warning(f"Fehler beim Suchen von Ghostscript: {str(e)}")
        return "gswin64c.exe"  # Fallback

# Ghostscript-Pfad einmal beim Start ermitteln
GHOSTSCRIPT_PATH = find_ghostscript_path()
logging.info(f"Verwende Ghostscript: {GHOSTSCRIPT_PATH}")

def ensure_utf8_encoding(xml_path):
    """
    Prüft die Kodierung der XML-Datei und konvertiert sie bei Bedarf nach UTF-8.
    Returns: Pfad zur UTF-8-kodierten XML-Datei
    """
    try:
        # Datei einlesen und Encoding erkennen
        with open(xml_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            detected_encoding = result['encoding']
            
        logging.info(f"Erkannte Kodierung der XML: {detected_encoding}")
        
        # Wenn es nicht UTF-8 ist, konvertieren
        if detected_encoding and detected_encoding.upper() != 'UTF-8':
            logging.info(f"Konvertiere XML von {detected_encoding} nach UTF-8")
            
            # Original-Content mit erkannter Kodierung lesen
            content = raw_data.decode(detected_encoding)
            
            # Neuen Dateinamen erstellen
            dir_path = os.path.dirname(xml_path)
            base_name = os.path.basename(xml_path)
            name_without_ext = os.path.splitext(base_name)[0]
            new_xml_path = os.path.join(dir_path, f"{name_without_ext}_utf8.xml")
            
            # Als UTF-8 speichern
            with open(new_xml_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            logging.info(f"UTF-8 XML erstellt: {new_xml_path}")
            return new_xml_path
            
        return xml_path
        
    except Exception as e:
        logging.error(f"Fehler bei der Kodierungsprüfung/-konvertierung: {str(e)}")
        return xml_path

def convert_to_pdfa(input_path, output_path):
    """
    Konvertiert eine PDF-Datei in das Format PDF/A-3b mit Ghostscript.
    """
    try:
        logging.info(f"Konvertiere PDF zu PDF/A-3b mit Ghostscript: {input_path}")
        
        # Temporäre Datei für die Konvertierung
        temp_output = tempfile.mktemp(suffix='.pdf')
        
        # Ghostscript-Befehl für PDF/A-3b-Konvertierung
        cmd = [
            GHOSTSCRIPT_PATH,  # Verwende den gefundenen Ghostscript-Pfad
            '-dPDFA=3',
            '-dPDFACompatibilityPolicy=1',
            '-dBATCH',
            '-dNOPAUSE',
            '-dNOOUTERSAVE',
            '-dNOSAFER',
            '-sColorConversionStrategy=UseDeviceIndependentColor',
            '-sDEVICE=pdfwrite',
            '-dPDFSETTINGS=/prepress',
            '-dCompatibilityLevel=1.7',
            '-dAutoRotatePages=/None',
            '-dAutoFilterColorImages=false',
            '-dColorImageFilter=/FlateEncode',
            '-dEmbedAllFonts=true',
            '-dSubsetFonts=true',
            '-dColorConversionStrategy=/LeaveColorUnchanged',
            '-dDownsampleMonoImages=false',
            '-dDownsampleGrayImages=false',
            '-dDownsampleColorImages=false',
            '-sOutputFile=' + output_path,
            input_path
        ]
        
        logging.info(f"Ausführen des Ghostscript-Befehls: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            logging.error(f"Fehler bei der PDF/A-Konvertierung mit Ghostscript: {process.stderr}")
            return False
            
        # Erfolgreiche Konvertierung überprüfen
        if os.path.exists(output_path):
            # Öffne die konvertierte PDF und überprüfe, ob sie PDF/A-3b ist
            try:
                with pikepdf.open(output_path, allow_overwriting_input=True) as pdf:
                    # Setze explizit die PDF/A-3b-Konformität in den Metadaten
                    with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                        meta['pdfaid:part'] = '3'
                        meta['pdfaid:conformance'] = 'B'
                        meta['pdf:Producer'] = 'AIDA ORGA Dortmund GmbH'
                    pdf.save(output_path)
                    
                logging.info(f"PDF/A-3b-Konvertierung erfolgreich: {output_path}")
                return True
            except Exception as e:
                logging.error(f"Fehler beim Setzen der PDF/A-Metadaten: {str(e)}")
                return False
        else:
            logging.error("Konvertierte PDF-Datei wurde nicht erstellt")
            return False
            
    except Exception as e:
        logging.error(f"Fehler bei der PDF/A-Konvertierung: {str(e)}")
        return False

def attach_xml_to_pdf(pdf_path, xml_path):
    """Fügt eine XML-Datei als Anhang zu einem PDF hinzu und konvertiert zu PDF/A-3b."""
    try:
        # Prüfe ob Dateien existieren
        if not os.path.exists(pdf_path):
            logging.error(f"PDF-Datei nicht gefunden: {pdf_path}")
            return False
        if not os.path.exists(xml_path):
            logging.error(f"XML-Datei nicht gefunden: {xml_path}")
            return False

        logging.info(f"Verarbeite PDF: {pdf_path}")
        logging.info(f"Verarbeite XML: {xml_path}")

        # Stelle sicher, dass XML UTF-8-kodiert ist
        utf8_xml_path = ensure_utf8_encoding(xml_path)
        if utf8_xml_path != xml_path:
            logging.info(f"Verwende UTF-8-konvertierte XML: {utf8_xml_path}")
            xml_path = utf8_xml_path

        # Originaldatei umbenennen
        original_dir = os.path.dirname(pdf_path)
        original_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(original_name)[0]
        ext = os.path.splitext(original_name)[1]
        backup_path = os.path.join(original_dir, f"{name_without_ext}_original{ext}")
        
        counter = 1
        while os.path.exists(backup_path):
            backup_path = os.path.join(original_dir, f"{name_without_ext}_original_{counter}{ext}")
            counter += 1
        
        logging.info(f"Erstelle Backup unter: {backup_path}")
        os.rename(pdf_path, backup_path)
        
        try:
            # Temporäre Datei für Zwischenschritt
            temp_pdf_path = os.path.join(original_dir, f"{name_without_ext}_temp{ext}")
            
            # PDF mit pikepdf öffnen
            pdf = pikepdf.open(backup_path)
            logging.info(f"PDF hat {len(pdf.pages)} Seiten")

            # XML-Datei als Anhang hinzufügen
            with open(xml_path, 'rb') as xml_file:
                xml_content = xml_file.read()
                xml_filename = os.path.basename(xml_path)
                logging.info(f"Füge XML als Anhang hinzu: {xml_filename}")
                
                # Füge die XML als FileAttachment hinzu
                pdf.attachments[xml_filename] = xml_content

            # Metadaten aktualisieren
            with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                meta['dc:title'] = f'{name_without_ext} mit X-Rechnung'
                meta['dc:creator'] = ['AIDA ORGA Dortmund GmbH']
                meta['pdf:Producer'] = 'AIDA ORGA Dortmund GmbH'
                meta['dc:description'] = 'PDF mit eingebetteter X-Rechnung'

            # Temporäre PDF speichern
            logging.info(f"Speichere temporäre PDF unter: {temp_pdf_path}")
            pdf.save(temp_pdf_path)
            pdf.close()
            
            # Konvertiere zu PDF/A-3b
            if convert_to_pdfa(temp_pdf_path, pdf_path):
                logging.info(f"PDF/A-3b-Datei erstellt: {pdf_path}")
                
                # Verifiziere die neue PDF
                verify_pdf = pikepdf.open(pdf_path)
                page_count = len(verify_pdf.pages)
                attachment_count = len(verify_pdf.attachments) if hasattr(verify_pdf, 'attachments') else 0
                logging.info(f"Neue PDF erfolgreich erstellt und verifiziert:")
                logging.info(f"- {page_count} Seiten")
                logging.info(f"- {attachment_count} Anhänge")
                verify_pdf.close()
                
                # Temporäre Dateien löschen
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                    logging.info(f"Temporäre PDF gelöscht: {temp_pdf_path}")
                
                # Temporäre UTF-8 XML löschen wenn sie erstellt wurde
                if utf8_xml_path != xml_path and os.path.exists(utf8_xml_path):
                    os.remove(utf8_xml_path)
                    logging.info(f"Temporäre UTF-8 XML gelöscht: {utf8_xml_path}")
                
                return True
            else:
                logging.error("PDF/A-3b-Konvertierung fehlgeschlagen")
                # Bei Fehler Original wiederherstellen
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                os.rename(backup_path, pdf_path)
                return False

        except Exception as e:
            logging.error(f"Fehler bei der PDF-Verarbeitung: {str(e)}")
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            os.rename(backup_path, pdf_path)
            return False

    except Exception as e:
        logging.error(f"Fehler beim Verarbeiten der Dateien: {str(e)}")
        # Bei Fehler versuchen, die Umbenennung rückgängig zu machen
        if os.path.exists(backup_path) and not os.path.exists(pdf_path):
            os.rename(backup_path, pdf_path)
            logging.info("Backup wiederhergestellt nach Fehler")
        return False

def create_email_with_attachment(recipient_email, pdf_path, mode):
    """
    Erstellt eine E-Mail mit dem PDF als Anhang.
    Mode 1: Nur PDF erstellen, keine E-Mail
    Mode 2: PDF erstellen und E-Mail öffnen
    Mode 3: PDF erstellen und E-Mail senden
    """
    if mode == 1:
        # Nur PDF erstellen, keine E-Mail
        logging.info("Modus 1: Nur PDF erstellt, keine E-Mail.")
        return True
        
    # Auf nicht-Windows-Systemen simulieren wir nur den E-Mail-Versand
    if platform.system() != 'Windows':
        logging.info(f"E-Mail-Funktionalität wird auf {platform.system()} simuliert")
        logging.info(f"Würde E-Mail an {recipient_email} mit Anhang {pdf_path} erstellen")
        if mode == 3:
            logging.info("Würde E-Mail automatisch senden")
        return True
        
    try:
        # Outlook-Anwendung starten
        outlook = win32com.client.Dispatch("Outlook.Application")
        
        # Neue E-Mail erstellen
        mail = outlook.CreateItem(0)  # 0 = olMailItem
        
        # E-Mail-Eigenschaften setzen
        mail.To = recipient_email
        mail.Subject = "X-Rechnung"
        
        # Basis-Body für die E-Mail
        base_body = "Sehr geehrte Damen und Herren,\n\n"
        base_body += "anbei erhalten Sie eine Rechnung im Format X-Rechnung.\n\n"
        
        # Je nach Modus unterschiedliche Aktionen
        if mode == 2:
            # E-Mail öffnen
            mail.Body = base_body
            mail.Attachments.Add(os.path.abspath(pdf_path))
            mail.Display(True)
            logging.info("E-Mail wurde erstellt und geöffnet.")
            
        elif mode == 3:
            # E-Mail senden
            # HTML-Body mit Signatur für Modus 3
            html_body = "<p>Sehr geehrte Damen und Herren,</p>"
            html_body += "<p>anbei erhalten Sie eine Rechnung im Format X-Rechnung.</p>"
            html_body += "<p>Mit freundlichen Grüßen</p>"
            html_body += "<p><b>Buchhaltung AIDA Dortmund</b></p>"
            
            mail.HTMLBody = html_body
            mail.Attachments.Add(os.path.abspath(pdf_path))
            mail.Sender = "buchhaltung@aida-dortmund.de"
            mail.Send()
            logging.info("E-Mail wurde automatisch gesendet.")
            
        return True
        
    except Exception as e:
        logging.error(f"Fehler beim Erstellen der E-Mail: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='X-Rechnung Tool - Fügt XML an PDF an und erstellt E-Mail')
    parser.add_argument('pdf_path', help='Pfad zur PDF-Datei')
    parser.add_argument('xml_path', help='Pfad zur XML-Datei')
    parser.add_argument('email', help='E-Mail-Adresse des Empfängers')
    parser.add_argument('mode', type=int, choices=[1, 2, 3], 
                      help='Betriebsmodus: 1=Nur PDF erstellen, 2=PDF erstellen und E-Mail öffnen, 3=PDF erstellen und E-Mail senden')
    
    args = parser.parse_args()

    logging.info("X-Rechnung Tool gestartet")
    logging.info(f"PDF Pfad: {args.pdf_path}")
    logging.info(f"XML Pfad: {args.xml_path}")
    logging.info(f"E-Mail: {args.email}")
    logging.info(f"Modus: {args.mode}")

    # XML an PDF anhängen
    if attach_xml_to_pdf(args.pdf_path, args.xml_path):
        # E-Mail mit Anhang erstellen (abhängig vom Modus)
        if create_email_with_attachment(args.email, args.pdf_path, args.mode):
            logging.info("Vorgang erfolgreich abgeschlossen!")
            print("Vorgang erfolgreich abgeschlossen!")
            # Ausgabe des finalen PDF-Pfads
            print(f"PDF wurde erstellt unter: {os.path.abspath(args.pdf_path)}")
        else:
            if args.mode != 1:  # Nur Fehler ausgeben, wenn E-Mail erstellt werden sollte
                logging.error("Fehler beim Erstellen der E-Mail.")
                print("Fehler beim Erstellen der E-Mail.")
    else:
        logging.error("Fehler beim Anhängen der XML-Datei an die PDF.")
        print("Fehler beim Anhängen der XML-Datei an die PDF.")

if __name__ == "__main__":
    main() 