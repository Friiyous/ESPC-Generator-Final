"""
WhatsApp Integration Module
"""

import requests
import os
from twilio.rest import Client
from datetime import datetime


class WhatsAppIntegration:
    def __init__(self):
        self.twilio_sid = os.environ.get("TWILIO_SID", "")
        self.twilio_token = os.environ.get("TWILIO_TOKEN", "")
        self.twilio_number = os.environ.get("TWILIO_NUMBER", "")
        self.recipient_numbers = os.environ.get("WHATSAPP_NUMBERS", "").split(",")

    def send_whatsapp_message(self, message, document_path=None):
        """Envoyer un message WhatsApp avec option de document"""
        try:
            client = Client(self.twilio_sid, self.twilio_token)

            for number in self.recipient_numbers:
                if number.strip():
                    # Envoyer le message
                    message_sid = client.messages.create(
                        body=message,
                        from_=f"whatsapp:{self.twilio_number}",
                        to=f"whatsapp:{number.strip()}",
                    )

                    # Si document fourni, l'envoyer aussi
                    if document_path and os.path.exists(document_path):
                        with open(document_path, "rb") as f:
                            media_sid = client.messages.create(
                                media_url=f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{f.read().encode('base64')}",
                                from_=f"whatsapp:{self.twilio_number}",
                                to=f"whatsapp:{number.strip()}",
                            )

            return True, "Messages envoyés avec succès"

        except Exception as e:
            return False, f"Erreur: {str(e)}"

    def send_document_notification(self, document_type, etablissement, periode):
        """Envoyer une notification pour un document généré"""
        message = f"""
📄 NOUVEAU DOCUMENT GÉNÉRÉ
        
Type: {document_type}
Établissement: {etablissement}
Période: {periode}
Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}

Vous pouvez consulter le document dans l'application ESPC Generator.
        """

        return self.send_whatsapp_message(message)

    def send_urgent_alert(self, alert_type, message, recipients=None):
        """Envoyer une alerte urgente"""
        if recipients:
            self.recipient_numbers = recipients

        alert_message = f"""
🚨 ALERTE URGENTE
        
Type: {alert_type}
Message: {message}
Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}

Action requise immédiate.
        """

        return self.send_whatsapp_message(alert_message)
