import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
MOVI_TOKEN = os.environ.get("MOVI_TOKEN")

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DO MOVIDESK ---


@app.route('/')
def index():
    return render_template('formulario_tef.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    try:
        # 1. PEGA TODOS OS DADOS BRUTOS DO FORMULÁRIO
        dados_brutos = request.form.to_dict(flat=False) 
        
        # 2. PRINT PARA DIAGNÓSTICO (VAI APARECER NO SEU TERMINAL)
        print("\n" + "="*50)
        print("DADOS RECEBIDOS DO FORMULÁRIO HTML:")
        print(json.dumps(dados_brutos, indent=4, ensure_ascii=False))
        print("="*50 + "\n")

        # 3. TRATAMENTO DOS DADOS PARA O PAYLOAD
        # (v[0] pega o primeiro valor de campos simples, o getlist pega todos os de checkbox)
        dados = {k: v[0] if v[0] else "" for k, v in dados_brutos.items()}
        admin_selecionadas = request.form.getlist('administradoras')
        bandeiras_selecionadas = request.form.getlist('bandeiras')
        

        resumo_formulario = (
            f"Solicitação via Formulário Web\n"
            f"----------------------------------------\n"
            f"👤 Responsável: {dados.get('responsavel')}\n"
            f"🏢 Razão Social: {dados.get('razao_social')}\n"
            f"📄 CNPJ: {dados.get('cnpj')}\n"
            f"📞 Telefone: {dados.get('telefone')}\n"
            f"📧 E-mail: {dados.get('email')}\n"
            f"💻 Terminal Lógico: {dados.get('Terminal Lógico')}\n"
            f"🔑 Cód. Afiliação: {dados.get('afiliacao')}\n"
            f"💳 Administradoras: {', '.join(admin_selecionadas)}\n"
            f"🚩 Bandeiras: {', '.join(bandeiras_selecionadas)}"
        )
        # Montagem do Payload idêntica ao sucesso do manual
        ticket_payload = {
            "type": 2, 
            "subject": f"Solicitação TEF - {dados.get('razao_social')}",
            "status": "Novo",
            "origin": 2,
            "serviceFirstLevelId": 1290660,
            "serviceFirstLevel": "TEF",
            "serviceSecondLevel": "Implantação ", # Mantido o espaço conforme manual
            "createdBy": {
                "id": "1665634567"
            },
            "clients": [
                {
                    "id": "1915669336",
                    "personType": 1
                }
            ],
            "actions": [
                {
                    "type": 2,
                    "origin": 0,
                    "description": resumo_formulario # Aqui entra o resumo que criamos acima
                }
            ],
            "customFieldValues": [
                {
                    "customFieldId": 242386, # CNPJ
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(dados.get('cnpj'))
                },
                {
                    "customFieldId": 242387, # Razão Social
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(dados.get('razao_social'))
                },
                {
                    "customFieldId": 242388, # Nome Fantasia
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(dados.get('responsavel'))
                },
                {
                    "customFieldId": 242389, # Telefone
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(dados.get('telefone'))
                },
                {
                    "customFieldId": 242390, # E-mail
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(dados.get('email'))
                },
                {
                    "customFieldId": 242391, # Adquirente (Campo de Seleção)
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "items": [
                        { "customFieldItem": dados.get('administradoras') }
                    ]
                },

                {
    "customFieldId": 242393, # ID que vimos na imagem image_91c5fe.png
    "customFieldRuleId": 127968,
    "line": 1,
    "value": str(dados.get('Terminal Lógico', '')) # 'Terminal Lógico' é o nome que vem do HTML
},
                {
                    "customFieldId": 242392, # Código de Afiliação
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(dados.get('afiliacao'))
                },
                {
                    "customFieldId": 242399, # Bandeiras (Múltipla Escolha)
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "items": [
                        { "customFieldItem": item } for item in request.form.getlist('bandeiras')
                    ]
                }
            ]
        }

        # Log para conferência no terminal
        print("\n" + "="*60)
        print("ENVIANDO PAYLOAD COMPLETO:")
        print(json.dumps(ticket_payload, indent=4, ensure_ascii=False))
        print("="*60 + "\n")

        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            MOVI_API_URL, 
            data=json.dumps(ticket_payload), 
            headers=headers,
            timeout=15
        )
 
        if response.status_code in [200, 201]:
            protocolo = response.json().get('protocol')
            print(f"SUCESSO! Ticket: {protocolo}")
            return jsonify({"success": True, "protocol": protocolo})
        else:
            print(f"ERRO API ({response.status_code}): {response.text}")
            return jsonify({"success": False, "error": response.text})

    except Exception as e:
        print(f"ERRO NO SERVIDOR: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)