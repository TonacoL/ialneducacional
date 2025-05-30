import openai
import os
from flask import Flask, request
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
ZAPI_URL = os.getenv('ZAPI_URL')

@app.route('/webhook', methods=['POST'])
def responder():
    data = request.json
    print("Recebido no webhook:", data)

    mensagem_cliente = data.get('text', {}).get('message')
    telefone_cliente = data.get('phone')

    if not mensagem_cliente or not telefone_cliente:
        return {"error": "Dados incompletos"}, 400

    try:
        resposta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "Você é uma atendente virtual carinhosa e profissional. "
                    "Responda sempre com empatia e clareza. Não passe valores. "
                    "Coleta as seguintes informações: tipo de trabalho, prazo, norma, dúvidas, etc. "
                    "Depois, diga que a equipe humana dará continuidade."
                )},
                {"role": "user", "content": mensagem_cliente}
            ]
        )
        resposta_texto = resposta.choices[0].message.content

    except Exception as e:
        print(f"Erro na OpenAI: {e}")
        resposta_texto = (
            "Estamos passando por instabilidades no atendimento automático. "
            "Nossa equipe humana dará continuidade em breve."
        )

    try:
        envio = requests.post(ZAPI_URL, json={
            "phone": telefone_cliente,
            "message": resposta_texto
        })
        print("Resposta do envio WhatsApp:", envio.status_code, envio.text)

    except Exception as e:
        print(f"Erro ao enviar mensagem para WhatsApp: {e}")

    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
