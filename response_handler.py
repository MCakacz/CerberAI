import smtplib
from email.mime.text import MIMEText
from config import SMTP_CONFIG, ADMIN_EMAIL
import openai

class ResponseHandler:
    @staticmethod
    def send_alert(command: str, closest_match: str, confidence: float):
        # Generuj interpretację AI (opcjonalne)
        analysis = "Brak analizy (brak klucza OpenAI)" 
        if OPENAI_API_KEY:
            prompt = f"Wyjaśnij zagrożenie: {command} (podobne do {closest_match})"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            analysis = response.choices[0].message.content

        # Wyślij email
        msg = MIMEText(f"""
        Komenda: {command}
        Podobieństwo do: {closest_match}
        Pewność: {confidence:.2f}%
        
        Analiza AI:
        {analysis}
        """)
        msg["Subject"] = "⚠️ CerberAI Alert"
        msg["From"] = SMTP_CONFIG["sender"]
        msg["To"] = ADMIN_EMAIL

        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)