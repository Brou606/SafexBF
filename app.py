# from flask import Flask, render_template, request, send_file
# import uuid
# import hashlib
# import qrcode
# import os
# import xlsxwriter
# import shutil

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'

# def create_new_folder():
#     folder_count = len([name for name in os.listdir('images') if os.path.isdir(os.path.join('images', name))])
#     folder_name = f"images_{folder_count + 1}"  # Nom du dossier basé sur le nombre de dossiers existants
#     folder_path = os.path.join('images', folder_name)
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#     return folder_path

# def generate_uuids(num):
#     return [str(uuid.uuid4()) for _ in range(num)]

# def generate_qr_codes(uuids, folder_path):
#     qr_codes = []
#     for i, uuid_str in enumerate(uuids, start=1):
#         sha1 = hashlib.sha1(uuid_str.encode()).hexdigest()
#         qr = qrcode.make(sha1)
#         filename = f"code_{i}.png"
#         qr.save(os.path.join(folder_path, filename))
#         qr_codes.append(filename)
#     return qr_codes

# def generate_excel(uuids, qr_codes, folder_path):
#     excel_path = os.path.join(folder_path, 'codes.xlsx')
#     workbook = xlsxwriter.Workbook(excel_path)
#     worksheet = workbook.add_worksheet()

#     headers = ['UUID', 'Identifiant', 'Hash SHA1', 'Nom du QR Code']
#     for col, header in enumerate(headers):
#         worksheet.write(0, col, header)

#     for row, (uuid_str, qr_code) in enumerate(zip(uuids, qr_codes), start=1):
#         identifier = uuid_str.replace('-', '')[:8]
#         sha1 = hashlib.sha1(uuid_str.encode()).hexdigest()
#         worksheet.write(row, 0, uuid_str)
#         worksheet.write(row, 1, identifier)
#         worksheet.write(row, 2, sha1)
#         worksheet.write(row, 3, qr_code)

#     workbook.close()
#     return excel_path

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         num_qr = int(request.form['num_qr'])
#         uuids = generate_uuids(num_qr)
#         folder_path = create_new_folder()
#         qr_codes = generate_qr_codes(uuids, folder_path)
#         excel_path = generate_excel(uuids, qr_codes, folder_path)

#         # Créer le dossier ZIP et y ajouter les fichiers
#         zip_filename = f"{folder_path}.zip"
#         shutil.make_archive(folder_path, 'zip', folder_path)

#         # Supprimer le dossier original après avoir créé le ZIP
#         shutil.rmtree(folder_path)

#         return send_file(zip_filename, as_attachment=True, download_name='codes.zip')

#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)







from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import uuid
import hashlib
import qrcode
import os
import xlsxwriter
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://SafexBF-35303439632d:4rxyxp70z3@sdb-68.hosting.stackcp.net/SafexBF'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    quota_mensuel = db.Column(db.Integer, nullable=False, default=3000)

def create_new_folder():
    folder_count = len([name for name in os.listdir('images') if os.path.isdir(os.path.join('images', name))])
    folder_name = f"images_{folder_count + 1}"  # Nom du dossier basé sur le nombre de dossiers existants
    folder_path = os.path.join('images', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def generate_uuids(num):
    return [str(uuid.uuid4()) for _ in range(num)]

def generate_qr_codes(uuids, folder_path):
    qr_codes = []
    for i, uuid_str in enumerate(uuids, start=1):
        sha1 = hashlib.sha1(uuid_str.encode()).hexdigest()
        qr = qrcode.make(sha1)
        filename = f"code_{i}.png"
        qr.save(os.path.join(folder_path, filename))
        qr_codes.append(filename)
    return qr_codes

def generate_excel(uuids, qr_codes, folder_path):
    excel_path = os.path.join(folder_path, 'codes.xlsx')
    workbook = xlsxwriter.Workbook(excel_path)
    worksheet = workbook.add_worksheet()

    headers = ['UUID', 'Identifiant', 'Hash SHA1', 'Nom du QR Code']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, (uuid_str, qr_code) in enumerate(zip(uuids, qr_codes), start=1):
        identifier = uuid_str.replace('-', '')[:8]
        sha1 = hashlib.sha1(uuid_str.encode()).hexdigest()
        worksheet.write(row, 0, uuid_str)
        worksheet.write(row, 1, identifier)
        worksheet.write(row, 2, sha1)
        worksheet.write(row, 3, qr_code)

    workbook.close()
    return excel_path

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        nouvel_utilisateur = Utilisateur(username=username, email=email, password=hashed_password)
        db.session.add(nouvel_utilisateur)
        db.session.commit()

        return redirect(url_for('connexion'))

    return render_template('inscription.html')

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        utilisateur = Utilisateur.query.filter_by(username=username).first()

        if utilisateur and bcrypt.check_password_hash(utilisateur.password, password):
            session['utilisateur_id'] = utilisateur.id
            return redirect(url_for('index'))
        else:
            return render_template('connexion.html', message='Nom d\'utilisateur ou mot de passe incorrect.')

    return render_template('connexion.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'utilisateur_id' not in session:
        return redirect(url_for('connexion'))

    utilisateur = Utilisateur.query.get(session['utilisateur_id'])

    if request.method == 'POST':
        if utilisateur.quota_mensuel <= 0:
            return render_template('quota.html')

        num_qr = int(request.form['num_qr'])

        if num_qr > utilisateur.quota_mensuel:
            return render_template('quota.html')

        utilisateur.quota_mensuel -= num_qr
        db.session.commit()

        uuids = generate_uuids(num_qr)
        folder_path = create_new_folder()
        qr_codes = generate_qr_codes(uuids, folder_path)
        excel_path = generate_excel(uuids, qr_codes, folder_path)

        # Créer le dossier ZIP et y ajouter les fichiers
        zip_filename = f"{folder_path}.zip"
        shutil.make_archive(folder_path, 'zip', folder_path)

        # Supprimer le dossier original après avoir créé le ZIP
        shutil.rmtree(folder_path)

        return send_file(zip_filename, as_attachment=True, download_name='codes.zip')

    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
