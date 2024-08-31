import json
import requests
from datetime import datetime, timezone,timedelta
import os



def pagar_com_pix(nome,email,cpf):
    agora = datetime.now(timezone.utc)
    data_expiracao = agora + timedelta(minutes=30)
    
    url = "https://api.pagseguro.com/orders"

    headers = {
        "accept": "*/*",        
        "Authorization": "Bearer 80eee03f-fabb-4c81-bd8f-bacfd70c53cddd29222947a8b89fef95438c0c84f6679858-601e-4391-a268-c4033d1e7013",
        "Content-Type": "application/json"
    }

    body = json.dumps({
        "reference_id": "OC-" + agora.strftime('%d/%m/%Y'),
        "amount": {
            "value": 500,  # valor em centavos (R$ 5,00)
            "currency": "BRL"
        },
        "customer": {
            "name": nome,
            "email": email,
            "tax_id": cpf,
            "phones": [
                {
                    "country": "55",
                    "area": "21",
                    "number": "994280064",
                    "type": "MOBILE"
                }
            ]
        },
        "items": [
            {
                "name": "QR Code",
                "quantity": 1,
                "unit_amount": 500  # valor em centavos
            }
        ],
        "qr_codes": [
            {
                "amount": {
                    "value": 500  # valor em centavos
                },
                "expiration_date": data_expiracao.isoformat()
            }
        ],
        "shipping": {
            "address": {
                "street": "Julio Lopes",
                "number": "225",
                "complement": "casa 1",
                "locality": "Santa Rita",
                "city": "Mendes",
                "region_code": "RJ",
                "country": "BRA",
                "postal_code": "26700000"
            }
        },
        "notification_urls": [
            "https://meusite.com/notificacoes"
        ]
    })
    
    response = requests.post(url,data=body,headers=headers)
    print(response.status_code)
    if response.status_code == 201:
        response_data = response.json()
        charge_id = response_data['id']
        img_qrCode = response_data['qr_codes'][0]['links'][0]['href']
        link_qrCode = response_data['qr_codes'][0]['text']
        expiration_date = response_data['qr_codes'][0]['expiration_date']
        return charge_id, link_qrCode, img_qrCode,expiration_date
    else:
        print(f"Erro ao criar a ordem de pagamento: {response.status_code}")
        print(f"Detalhes do erro: {response.text}")
        return None






