
import qrcode
from flask import Flask, render_template, request, redirect, url_for,jsonify
import requests
from PIL import Image
from model.icon import Icon
from model.icon_list import icon_list
import os
from model.pagamento import pagar_com_pix,TOKEN
from flask_wtf.csrf import CSRFProtect



app = Flask('__name__', template_folder="view/templates", static_folder='view/static')
icones = []

app.config['SECRET_KEY'] = 'Jefferson_pagseguro'

csrf = CSRFProtect(app)
# Iterando sobre os itens do dicionário
for key, value in icon_list.items():
    name = value['name']
    link = value['link']
    icones.append(Icon(name, link))


@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        link = request.form['link']
        icon_name = request.form['icon']

        icon_obj = next((icon for icon in icones if icon.name == icon_name), None)

        if icon_obj:
            # Realiza o pagamento e obtém o charge_id
            charge_id = pagar_com_pix()
            
            # Verifica o status do pagamento usando o charge_id          
            try:
                response = requests.get(f"https://qrcode-xmk8.onrender.com/verificar_pagamento/{charge_id}")
                response_data = response.json()
                img_qrCode = response_data.get('img_qrCode', '')
                link_qrCode = response_data.get('link_qrCode', '')
                status = response_data.get('status', '')

                if status != 'PAY':
                    # Verifica se img_qrCode e link_qrCode são válidos
                    img_qrCode = img_qrCode if img_qrCode else ''
                    link_qrCode = link_qrCode if link_qrCode else ''
                    return render_template('pagamento.html', img_qrCode=img_qrCode, link_qrCode=link_qrCode, charge_id=charge_id,link = link,icon = icon_obj.to_dict())
                
                return makeQrCode()
            except Exception as e:
                print("Erro ao verificar pagamento:", e)
                
                return jsonify({'error': 'Erro ao verificar pagamento'}), 500
     
    return render_template('index.html', icones=icones)

@app.route('/make_qr_code')
def makeQrCode():
    link = request.args.get('link')
    icon_name = request.args.get('icon_name')
    icon_endereco = request.args.get('icon_endereco')

    # Create an instance of Icon with the provided parameters
    icon = Icon(name=icon_name, endereco=icon_endereco)

    logo = Image.open('view/static/' + icon.endereco)

    basewidth = 100
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize))

    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    QRcode.add_data(link)
    QRcode.make()

    QRcolor = 'Black'
    QRimg = QRcode.make_image(fill_color=QRcolor, back_color="white").convert('RGB')

    pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)

    image_filename = 'QRCode_' + icon.name + '.png'
    image_path = os.path.join(app.static_folder, 'qrcodes/', image_filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    QRimg.save(image_path)

    image_url = 'qrcodes/' + image_filename

    print(image_url)

    return render_template('qrcode_download.html',image_url = image_url)



@app.route('/verificar_pagamento/<charge_id>', methods=['GET'])
def verificar_pagamento_pix(charge_id):
    url = f"https://sandbox.api.pagseguro.com/orders/{charge_id}"

    headers = {
        "accept": "*/*",
        "Authorization": "Bearer 80eee03f-fabb-4c81-bd8f-bacfd70c53cddd29222947a8b89fef95438c0c84f6679858-601e-4391-a268-c4033d1e7013",
        "content-type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    # Verificar se a resposta foi bem-sucedida
    if response.status_code == 200:
        response_data = response.json()

        # Extraia os dados necessários, com tratamento para ausência de campos
        img_qrCode = response_data.get('qr_codes', [{}])[0].get('links', [{}])[0].get('href', '')
        link_qrCode = response_data.get('qr_codes', [{}])[0].get('text', '')
        status = response_data.get('links', [{}])[1].get('rel', '')

        return jsonify({'img_qrCode': img_qrCode, 'link_qrCode': link_qrCode, 'status': status, 'charge_id': charge_id})
    else:
        # Retornar um erro apropriado se a resposta não for bem-sucedida
        return jsonify({'error': 'Erro ao verificar pagamento'}), response.status_code


if __name__== '__main__':
    app.run()