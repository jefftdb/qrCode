import json
import requests
from datetime import datetime, timezone,timedelta


def getPublicKey():

    url = "https://sandbox.api.assinaturas.pagseguro.com/public-keys"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "7f19e2d0-2774-44e5-8d0e-7efefe8be849557ab247436f91b32802981b2e99fd681789-cfc4-47a4-a604-7f1c542bd135"
    }

    body = json.dumps({
        "type":"carrd"
    })

    response = requests.put(url, headers=headers,data=body)

    
    return response.json()['public_key']



def pagar_com_pix():
    agora = datetime.now(timezone.utc)
    data_expiracao = agora + timedelta(minutes=30)
    
    url = "https://sandbox.api.pagseguro.com/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "7f19e2d0-2774-44e5-8d0e-7efefe8be849557ab247436f91b32802981b2e99fd681789-cfc4-47a4-a604-7f1c542bd135"
    }

    body = json.dumps({
    "reference_id": "ex-00001",
    "customer": {
        "name": 'Jefferson',
        "email": 'Jefftdb2@gmail.com',
        "tax_id": '13107000795',
        "phones": [
            {
                "country": "55",
                "area": '21',
                "number": '994280064',
                "type": "MOBILE"
            }
        ]
    },
    "items": [
        {
            "name": 'QR Code',
            "quantity": 1,
            "unit_amount": 1
        }
    ],
    "qr_codes": [
        {
            "amount": {
                "value": 1 
            },
            "expiration_date": data_expiracao.isoformat(),
        }
    ],
         
    "shipping": {
        "address": {
            "street": 'Julio Lopes',
            "number": '225',
            "complement": 'casa 1',
            "locality": 'Santa Rita',
            "city": 'Mendes',
            "region_code": 'RJ',
            "country": "BRA",
            "postal_code": '26700000' # Sem hífen, apenas 8 dígitos
        }
    },
    "notification_urls": [
        "https://meusite.com/notificacoes"
    ],
})
    
    response = requests.post(url, headers=headers, data=body)
    response_data = response.json()

    print(response_data)

    img_qrCode = response_data['qr_codes'][0]['links'][0]['href']
    link_qrCode = response_data['qr_codes'][0]['text']
    return  f'<img src="{img_qrCode}"> {link_qrCode}'  