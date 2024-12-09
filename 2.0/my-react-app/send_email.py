# backend/send_email.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
import requests
from io import BytesIO
import os

def send_email_with_excel(to_email, client_id):
    # Obtener datos desde los endpoints
    tarifas_historicas_data = fetch_tarifas_historicas(client_id)
    tarifario_data = fetch_tarifario(client_id)

    # Crea un DataFrame de pandas para el archivo Excel
    tarifas_df = pd.DataFrame(tarifas_historicas_data)
    tarifario_df = pd.DataFrame(tarifario_data)

    # Guardar el DataFrame en un buffer de bytes en formato Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tarifas_df.to_excel(writer, sheet_name='Tarifas Historicas', index=False)
        tarifario_df.to_excel(writer, sheet_name='Tarifario', index=False)

    output.seek(0)  # Vuelve al principio del archivo en memoria

    # Configura el correo
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USER')  # Cambia esto por tu correo
    msg['To'] = to_email
    msg['Subject'] = 'Reporte de Tarifas'

    # Adjunta el archivo Excel
    attachment = MIMEApplication(output.read(), Name='reporte_tarifas.xlsx')
    attachment['Content-Disposition'] = 'attachment; filename="reporte_tarifas.xlsx"'
    msg.attach(attachment)

    # Envía el correo
    with smtplib.SMTP('smtp.example.com', 587) as server:  # Cambia esto por tu servidor SMTP
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))  # Cambia esto por tus credenciales
        server.send_message(msg)

def fetch_tarifas_historicas(client_id):
    url = f"http://127.0.0.1:5000/api/tarifas_historicas?fecha_movimiento={pd.Timestamp.now().isoformat()}"
    response = requests.get(url)
    response.raise_for_status()  # Lanza un error si la respuesta no es exitosa
    return response.json()

def fetch_tarifario(client_id):
    url = f"http://127.0.0.1:5000/api/tarifario?cliente={client_id}"
    response = requests.get(url)
    response.raise_for_status()  # Lanza un error si la respuesta no es exitosa
    return response.json()
