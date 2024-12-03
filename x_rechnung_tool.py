#!/usr/bin/env python3
import sys
import os
import logging
import pikepdf
import win32com.client
import argparse

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def create_email_with_attachment(email_address, attachment_path):
    """Öffnet eine neue E-Mail mit Anhang im Standard-Mail-Client."""
    try:
        if not os.path.exists(attachment_path):
            logging.error(f"Anhang nicht gefunden: {attachment_path}")
            return False

        logging.info(f"Erstelle E-Mail für: {email_address}")
        logging.info(f"Mit Anhang: {attachment_path}")
        
        # Absoluten Pfad verwenden
        abs_attachment_path = os.path.abspath(attachment_path)
        
        outlook = win32com.client.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)  # 0 = olMailItem
        mail.To = email_address
        mail.Subject = "X-Rechnung"
        mail.Attachments.Add(abs_attachment_path)
        mail.Display(True)  # True = zeige das Mail-Fenster an
        logging.info("E-Mail erfolgreich erstellt")
        return True
    except Exception as e:
        logging.error(f"Fehler beim Erstellen der E-Mail: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='X-Rechnung Tool - Fügt XML an PDF an und erstellt E-Mail')
    parser.add_argument('pdf_path', help='Pfad zur PDF-Datei')
    parser.add_argument('xml_path', help='Pfad zur XML-Datei')
    parser.add_argument('email', help='E-Mail-Adresse des Empfängers')
    
    args = parser.parse_args()

    logging.info("X-Rechnung Tool gestartet")
    logging.info(f"PDF Pfad: {args.pdf_path}")
    logging.info(f"XML Pfad: {args.xml_path}")
    logging.info(f"E-Mail: {args.email}")

    # XML an PDF anhängen
    if attach_xml_to_pdf(args.pdf_path, args.xml_path):
        # E-Mail mit Anhang erstellen
        if create_email_with_attachment(args.email, args.pdf_path):
            logging.info("Vorgang erfolgreich abgeschlossen!")
            print("Vorgang erfolgreich abgeschlossen!")
        else:
            logging.error("Fehler beim Erstellen der E-Mail.")
            print("Fehler beim Erstellen der E-Mail.")
    else:
        logging.error("Fehler beim Anhängen der XML-Datei an die PDF.")
        print("Fehler beim Anhängen der XML-Datei an die PDF.")

if __name__ == "__main__":
    main() 