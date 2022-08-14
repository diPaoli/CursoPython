from __future__ import print_function

import os.path
from time import sleep

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth import default

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from email.message import EmailMessage



# escopo de autorização
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# faz a OAuth do app com o Gmail
# primeiro é preciso cadastrar o app no Google Cloud e adicionar a credencial.
# baixar o arquivo JSON para a mesma pasta deste projeto
def autorization():
    creds = None

    # usa o token já existente, ou cria um se não existir
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # pega a credencial do Gmail API
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # usa as credenciais para acessar o Gmail e mostrar as pastas cadastradas (labels)
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')




# envia um email e printa o ID da mensagem
def gmail_send_email(sender, to, sub, msg):
    # primeiro pega as credenciais
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # monta o email
        service = build('gmail', 'v1', credentials=creds)

        message = EmailMessage()
        message.set_content(msg)
        message['To'] = to
        message['From'] = sender
        message['Subject'] = sub

        # o objeto precisa ser codificado para b64
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        # envia o email
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


if __name__ == '__main__':
    remetente = 'mail_from@gmail.com'
    destinatario = 'mail_to@gmail.com'
    assunto = 'Your Subject'
    corpo = 'Body of the Email'
    while True:
        # envia 1 email a cada 5 segundos
        gmail_send_email(remetente, destinatario, assunto, corpo)
        sleep(5)


#if __name__ == '__main__':
    #autorization()