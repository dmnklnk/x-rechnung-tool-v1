#!/usr/bin/env python3
import sys
import os
import logging
import pikepdf
import win32com.client
import argparse
import chardet
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def attach_xml_to_pdf(pdf_path, xml_path):
    """Fügt eine XML-Datei als Anhang zu einem PDF hinzu."""
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
            with pdf.open_metadata() as meta:
                meta['dc:title'] = f'{name_without_ext} mit X-Rechnung'
                meta['dc:creator'] = 'X-Rechnung Tool'
                meta['pdf:Producer'] = 'X-Rechnung Tool v1.0'
                meta['dc:description'] = 'PDF mit eingebetteter X-Rechnung'

            # Neue PDF speichern
            logging.info(f"Speichere neue PDF unter: {pdf_path}")
            pdf.save(pdf_path)
            
            # Verifiziere die neue PDF
            verify_pdf = pikepdf.open(pdf_path)
            page_count = len(verify_pdf.pages)
            attachment_count = len(verify_pdf.attachments)
            logging.info(f"Neue PDF erfolgreich erstellt und verifiziert:")
            logging.info(f"- {page_count} Seiten")
            logging.info(f"- {attachment_count} Anhänge")
            verify_pdf.close()
            pdf.close()

            # Temporäre UTF-8 XML löschen wenn sie erstellt wurde
            if utf8_xml_path != xml_path and os.path.exists(utf8_xml_path):
                os.remove(utf8_xml_path)
                logging.info(f"Temporäre UTF-8 XML gelöscht: {utf8_xml_path}")

            return True

        except Exception as e:
            logging.error(f"Fehler bei der PDF-Verarbeitung: {str(e)}")
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

def create_email_with_attachment(email_address, attachment_path, mode):
    """
    Öffnet eine neue E-Mail mit Anhang im Standard-Mail-Client.
    mode: 1 = keine E-Mail, 2 = E-Mail anzeigen, 3 = E-Mail direkt senden
    """
    try:
        if mode == 1:
            logging.info("Modus 1: Keine E-Mail wird erstellt")
            return True
            
        if not os.path.exists(attachment_path):
            logging.error(f"Anhang nicht gefunden: {attachment_path}")
            return False

        logging.info(f"Erstelle E-Mail für: {email_address}")
        logging.info(f"Mit Anhang: {attachment_path}")
        
        # Absoluten Pfad verwenden
        abs_attachment_path = os.path.abspath(attachment_path)
        
        # PDF-Name ohne Pfad und Erweiterung extrahieren
        pdf_name = os.path.splitext(os.path.basename(attachment_path))[0]
        
        # Aktuelles Datum im Format DD.MM.YYYY
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        outlook = win32com.client.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)  # 0 = olMailItem
        mail.To = email_address
        mail.Subject = f"Rechnung {pdf_name} - {current_date}"
        
        # E-Mail-Body mit Formatierung
        mail.HTMLBody = """
        <p>Sehr geehrte Damen und Herren,</p>
        <p>angefügt erhalten Sie unsere Rechnung mit Bitte um Ausgleich.</p>
        """
        
        mail.Attachments.Add(abs_attachment_path)
        
        if mode == 2:
            mail.Display(True)  # E-Mail-Fenster anzeigen
            logging.info("E-Mail wurde zur Bearbeitung geöffnet")
        elif mode == 3:
            mail.Send()  # E-Mail direkt senden
            logging.info("E-Mail wurde automatisch versendet")
            
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