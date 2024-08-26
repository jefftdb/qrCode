import json
import requests
from datetime import datetime, timezone,timedelta
import os

TOKEN = os.getenv('TOKEN')

def pagar_com_pix():
    agora = datetime.now(timezone.utc)
    data_expiracao = agora + timedelta(minutes=30)
    
    url = "https://api.pagseguro.com/orders"

    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        "Authorization": "Bearer 80eee03f-fabb-4c81-bd8f-bacfd70c53cddd29222947a8b89fef95438c0c84f6679858-601e-4391-a268-c4033d1e7013" 
    }

    body = json.dumps({
        "reference_id": "ex-00001",
        "amount": {
            "value": 500,  # valor em centavos (R$ 5,00)
            "currency": "BRL"
        },
        "customer": {
            "name": "Jefferson",
            "email": "Jefftdb2@gmail.com",
            "tax_id": "13107000795",
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
    
    response = requests.post(url, headers=headers, data=body)
    response_data = response.json()
    
    # Tente capturar o ID correto a partir da resposta, pode ser que esteja em outro campo
    charge_id = response_data.get('id')  # Verifique se 'id' ou 'qr_codes' contém o charge_id correto
    
    
    return charge_id





