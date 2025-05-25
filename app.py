from flask import Flask, request
import requests
import openai
import os

app = Flask(__name__)
openai.api_key = 'OPENAI_API_KEY'  

ZAPI_URL = 'https://api.z-api.io/instances/3E1BCA9413A5C08CF9B0FECBD5821189/token/0515598C34FEFBF56AE5C047/send-text'

@app.route('/webhook', methods=['POST'])
def responder():
    data = request.json
    mensagem_cliente = data['message']
    telefone_cliente = data['phone']

    # Enviar mensagem para o ChatGPT
    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "Você é uma atendente virtual carinhosa e profissional. Responda sempre com empatia e clareza. Não passe valores. Coleta as seguintes informações: tipo de trabalho, prazo, norma, dúvidas, etc. Depois, diga que a equipe humana vai dar continuidade."
            },
            {"role": "user", "content": mensagem_cliente}
        ]
    )

    resposta_texto = resposta['choices'][0]['message']['content']

    # Enviar a resposta para o WhatsApp
    requests.post(ZAPI_URL, json={
        "phone": telefone_cliente,
        "message": resposta_texto
    })

    return "ok"

# >>> ESSA PARTE É A ALTERAÇÃO PARA FUNCIONAR NO RENDER:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
