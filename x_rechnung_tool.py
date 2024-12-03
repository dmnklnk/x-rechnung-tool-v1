#!/usr/bin/env python3
import sys
import os
from PyPDF2 import PdfReader, PdfWriter
import win32com.client
import argparse

def attach_xml_to_pdf(pdf_path, xml_path):
    """Fügt eine XML-Datei als Anhang zu einem PDF hinzu."""
    try:
        # Originaldatei umbenennen
        original_dir = os.path.dirname(pdf_path)
        original_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(original_name)[0]
        ext = os.path.splitext(original_name)[1]
        backup_path = os.path.join(original_dir, f"{name_without_ext}_original{ext}")
        
        # Wenn bereits eine Backup-Datei existiert, diese nicht überschreiben
        counter = 1
        while os.path.exists(backup_path):
            backup_path = os.path.join(original_dir, f"{name_without_ext}_original_{counter}{ext}")
            counter += 1
            
        os.rename(pdf_path, backup_path)
        
        # PDF lesen
        reader = PdfReader(backup_path)
        writer = PdfWriter()

        # Alle Seiten kopieren
        for page in reader.pages:
            writer.add_page(page)

        # XML-Datei als Anhang hinzufügen
        with open(xml_path, 'rb') as xml_file:
            xml_content = xml_file.read()
            writer.add_attachment(xml_path, xml_content)

        # Neue PDF am ursprünglichen Speicherort speichern
        with open(pdf_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Dateien: {str(e)}")
        # Bei Fehler versuchen, die Umbenennung rückgängig zu machen
        if os.path.exists(backup_path) and not os.path.exists(pdf_path):
            os.rename(backup_path, pdf_path)
        return False

def create_email_with_attachment(email_address, attachment_path):
    """Öffnet eine neue E-Mail mit Anhang im Standard-Mail-Client."""
    try:
        outlook = win32com.client.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)  # 0 = olMailItem
        mail.To = email_address
        mail.Subject = "X-Rechnung"
        mail.Attachments.Add(attachment_path)
        mail.Display(True)  # True = zeige das Mail-Fenster an
        return True
    except Exception as e:
        print(f"Fehler beim Erstellen der E-Mail: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='X-Rechnung Tool - Fügt XML an PDF an und erstellt E-Mail')
    parser.add_argument('pdf_path', help='Pfad zur PDF-Datei')
    parser.add_argument('xml_path', help='Pfad zur XML-Datei')
    parser.add_argument('email', help='E-Mail-Adresse des Empfängers')
    
    args = parser.parse_args()

    # XML an PDF anhängen
    if attach_xml_to_pdf(args.pdf_path, args.xml_path):
        # E-Mail mit Anhang erstellen
        if create_email_with_attachment(args.email, args.pdf_path):
            print("Vorgang erfolgreich abgeschlossen!")
            print(f"Original-PDF wurde gesichert mit Suffix '_original'")
        else:
            print("Fehler beim Erstellen der E-Mail.")
    else:
        print("Fehler beim Anhängen der XML-Datei an die PDF.")

if __name__ == "__main__":
    main() 