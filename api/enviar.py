import os
import json
import requests
from urllib.parse import parse_qs

MOVI_TOKEN = "2ebb185e-9444-4688-8a45-fadd1534353b"
MOVI_API_URL = f"https://api.movidesk.com/public/v1/tickets?token={MOVI_TOKEN}"

def handler(request):
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse JSON data from request.body
        data = json.loads(request.body.decode('utf-8'))
        
        print("\n" + "="*50)
        print("DADOS RECEBIDOS DO FORMULÁRIO HTML:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print("="*50 + "\n")

        # Extract data
        razao_social = data.get('razaoSocial', '')
        cnpj = data.get('cnpj', '')
        responsavel = data.get('responsavel', '')
        telefone = data.get('telefone', '')
        email = data.get('email', '')
        administradoras = data.get('administradoras', [])
        bandeiras = data.get('bandeiras', [])
        
        # For administradoras, take the first one or join names
        admin_nomes = [adm['nome'] for adm in administradoras]
        admin_selecionadas = admin_nomes
        # For the payload, perhaps take the first or something
        admin_principal = admin_nomes[0] if admin_nomes else ''
        
        # For Terminal Lógico, from the first admin's campos
        terminal_logico = ''
        if administradoras:
            campos = administradoras[0].get('campos', {})
            terminal_logico = campos.get('Terminal Lógico', '') or campos.get('Número Lógico', '') or campos.get('Cód. Estabelecimento', '')
        
        resumo_formulario = (
            f"Solicitação via Formulário Web\n"
            f"----------------------------------------\n"
            f"👤 Responsável: {responsavel}\n"
            f"🏢 Razão Social: {razao_social}\n"
            f"📄 CNPJ: {cnpj}\n"
            f"📞 Telefone: {telefone}\n"
            f"📧 E-mail: {email}\n"
            f"💻 Terminal Lógico: {terminal_logico}\n"
            f"🔑 Cód. Afiliação: \n"  # Not in data
            f"💳 Administradoras: {', '.join(admin_selecionadas)}\n"
            f"🚩 Bandeiras: {', '.join(bandeiras)}"
        )
        
        ticket_payload = {
            "type": 2, 
            "subject": f"Solicitação TEF - {razao_social}",
            "status": "Novo",
            "origin": 2,
            "serviceFirstLevelId": 1290660,
            "serviceFirstLevel": "TEF",
            "serviceSecondLevel": "Implantação ",
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
                    "description": resumo_formulario
                }
            ],
            "customFieldValues": [
                {
                    "customFieldId": 242386,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(cnpj)
                },
                {
                    "customFieldId": 242387,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(razao_social)
                },
                {
                    "customFieldId": 242388,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(responsavel)
                },
                {
                    "customFieldId": 242389,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(telefone)
                },
                {
                    "customFieldId": 242390,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(email)
                },
                {
                    "customFieldId": 242391,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "items": [
                        { "customFieldItem": admin_principal }
                    ]
                },
                {
                    "customFieldId": 242393,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": str(terminal_logico)
                },
                {
                    "customFieldId": 242392,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "value": ""  # afiliacao not provided
                },
                {
                    "customFieldId": 242399,
                    "customFieldRuleId": 127968,
                    "line": 1,
                    "items": [
                        { "customFieldItem": item } for item in bandeiras
                    ]
                }
            ]
        }

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
            return {
                'statusCode': 200,
                'body': json.dumps({"success": True, "protocol": protocolo})
            }
        else:
            print(f"ERRO API ({response.status_code}): {response.text}")
            return {
                'statusCode': 400,
                'body': json.dumps({"success": False, "error": response.text})
            }

    except Exception as e:
        print(f"ERRO NO SERVIDOR: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({"success": False, "error": str(e)})
        }