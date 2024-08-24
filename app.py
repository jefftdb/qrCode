
import qrcode
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
from model.icon import Icon
from model.icon_list import icon_list
import os
from model.pagamento import getPublicKey,pagar_com_pix
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
    data = {}
    data['publickey'] = getPublicKey()

    if request.method == 'POST':
        link = request.form['link']
        icon_name = request.form['icon']

        icon_obj = next((icon for icon in icones if icon.name == icon_name), None)

        if icon_obj:
            pagar_com_pix()
            return makeQrCode(link, icon_obj)

    return render_template('index.html', icones=icones, data= data)

def makeQrCode(link, icon):
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

    # taking color name from user
    QRcolor = 'Black'
  
    # adding color to QR code
    QRimg = QRcode.make_image(fill_color=QRcolor, back_color="white").convert('RGB')

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)

    # Supondo que QRimg seja o objeto da imagem gerada e `icon.name` o nome do ícone
    image_filename = 'QRCode_' + icon.name + '.png'

    # Caminho completo dentro da pasta static
    image_path = os.path.join(app.static_folder, 'qrcodes/', image_filename)

    # Crie o diretório 'qrcodes' dentro de 'static' se não existir
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    # Salvando a imagem
    QRimg.save(image_path)

    # Gerar a URL da imagem
    image_url = url_for('static', filename=os.path.join('qrcodes/', image_filename))

    # Retornando a tag <img> com a URL da imagem
    return f'<img src="{image_url}" alt="QR Code">'
