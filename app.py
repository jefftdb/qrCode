
import qrcode
from flask import Flask, render_template, request, redirect, url_for,jsonify
import requests
from PIL import Image
from model.icon import Icon
from model.icon_list import icon_list
import os
from model.pagamento import pagar_com_pix
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timezone



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
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['CPF']

        icon_obj = next((icon for icon in icones if icon.name == icon_name), None)

        if icon_obj:                       
                      
            try:
                # Realiza o pagamento e obtém o charge_id
                charge_id,link_qrCode,img_qrCode,expiration_date = pagar_com_pix(nome,email,cpf)
                
                return render_template('pagamento.html', img_qrCode=img_qrCode, link_qrCode=link_qrCode, charge_id=charge_id,link = link,icon = icon_obj.to_dict(),expiration_date = expiration_date)
    
                     
            except Exception as e:
                print("Erro ao verificar pagamento:", e)
                print('char_id: ',charge_id)
                print('link_qrcode:',link_qrCode)
                print('img_qrcode:',img_qrCode)
                print('data_expiration:', expiration_date)
                return jsonify({'error': 'Erro ao verificar pagamento'}), 500
     
    return render_template('index.html', icones=icones)

@app.route('/make_qr_code')
def makeQrCode():
    link = request.args.get('link')
    icon_name = request.args.get('icon_name')
    icon_endereco = request.args.get('icon_endereco')
    charge_id = request.args.get('charge_id')
    agora = datetime.now(timezone.utc)

    pagamento = verificar_pagamento_pix(charge_id)

    

    # Create an instance of Icon with the provided parameters
    icon = Icon(name=icon_name, endereco=icon_endereco)

    

    if icon.name == 'ban':
        QRcode = qrcode.make(link)

        image_filename = 'QRCode_' + icon.name + agora.strftime('%d/%m/%Y') + '.png'
        image_path = os.path.join(app.static_folder, 'qrcodes/', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        QRcode.save(image_path)
    
    else:
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

        image_filename = 'QRCode_' + icon.name + agora.strftime('%d/%m/%Y') + '.png'
        image_path = os.path.join(app.static_folder, 'qrcodes/', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        QRimg.save(image_path)
    

    image_url = 'qrcodes/' + image_filename

    print(image_url)

    return render_template('qrcode_download.html',image_url = image_url)

    


@app.route('/verificar_pagamento/<charge_id>', methods=['GET'])
def verificar_pagamento_pix(charge_id):
    url = f"https://api.pagseguro.com/orders/{charge_id}"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer 80eee03f-fabb-4c81-bd8f-bacfd70c53cddd29222947a8b89fef95438c0c84f6679858-601e-4391-a268-c4033d1e7013",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            response_data = response.json()

            # Adicionando logs de depuração
            print("Response JSON:", response_data)

            # Verifique se 'charges' está presente e é uma lista
            if 'charges' in response_data and isinstance(response_data['charges'], list):
                charges_data = response_data['charges'][0]  # Pegue o primeiro item da lista de 'charges'

                # Extração do status
                status = charges_data.get('status', 'Status não encontrado')

                # Extração dos dados do QR Code
                img_qrCode = response_data.get('qr_codes', [{}])[0].get('links', [{}])[0].get('href', '')
                link_qrCode = response_data.get('qr_codes', [{}])[0].get('text', '')

                return jsonify({'status': status, 'img_qrCode': img_qrCode, 'link_qrCode': link_qrCode, 'charge_id': charge_id})
            else:
                # 'charges' não foi encontrado ou não é uma lista
                print("Erro: 'charges' não está presente ou não é uma lista")
                return jsonify({'error': "'charges' não encontrado ou mal formatado"}), 500

        except (ValueError, IndexError) as e:
            # Tratamento de erro em caso de JSON mal formatado ou falta de dados esperados
            print("Erro ao processar resposta:", str(e))
            return jsonify({'error': f'Erro ao processar resposta: {str(e)}'}), 500
    else:
        # Caso a requisição não seja bem-sucedida
        print("Erro na requisição:", response.status_code)
        return jsonify({'error': 'Erro ao verificar pagamento'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)