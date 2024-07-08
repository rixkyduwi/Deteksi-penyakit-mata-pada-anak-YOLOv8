from flask import Flask,jsonify,request,session,render_template,g,send_from_directory,abort
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_bcrypt import Bcrypt
from datetime import timedelta,datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'deteksi_yolov8'
project_directory = os.path.abspath(os.path.dirname(__file__))
upload_folder = os.path.join(project_directory, 'static', 'upload')
detect_folder = os.path.join(project_directory, 'static', 'detect')
app.config['UPLOAD_FOLDER'] = upload_folder 
app.config['PROJECT_FOLDER'] = project_directory 
app.config['DETECT_FOLDER'] = detect_folder 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/deteksi_yolov8'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bukan rahasia')
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', b'asahdjhwquoyo192382qo')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'qwdu92y17dqsu81')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define the 'user_roles' class before 'User' class
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary='user_roles', 
                            primaryjoin='User.id == UserRoles.user_id',
                            secondaryjoin='Role.id == UserRoles.role_id',
                            backref=db.backref('users', lazy='dynamic'))
    fs_uniquifier = db.Column(db.String(64), unique=True)
    # One-to-One relationship with Profile
    profile = db.relationship('Profile', uselist=False, back_populates='user')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    full_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    phone_number = db.Column(db.String(20))
    bio = db.Column(db.Text)
    nama_anak = db.Column(db.String(255))
    usia_anak = db.Column(db.Integer )

    # Back reference to User
    user = db.relationship('User', back_populates='profile')

class History(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    nama_user = db.Column(db.String(225))    
    nama_anak = db.Column(db.String(225))   
    usia_anak = db.Column(db.Integer())
    hasil_diagnosa = db.Column(db.String(20))  
    file_deteksi = db.Column(db.String(225)) 
    tanggal_konsultasi = db.Column(db.String(225), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class Rekomendasi(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    nama = db.Column(db.String(225), unique=True) 
    pengobatan = db.Column(db.Text)  
    link_rekomendasi = db.Column(db.String(225))  
    def serialize(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'pengobatan': self.pengobatan,
            'link_rekomendasi': self.link_rekomendasi
        }


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=user_datastore, app=app)

jwt = JWTManager(app)
mysql = MySQL()
mysql.init_app(app)

# allow CORS biar api yang dibuat bisa dipake website lain
from flask_cors import CORS
# CORS(app, resources={r"/chatbot/*":  {"origins": ["https://","https://www"]}})
# Import rute dari modul-modul Anda

@app.route('/sitemap.xml')
def sitemap():
    # Logika untuk menghasilkan sitemap.xml
    # Misalnya, jika sitemap.xml adalah file statis, Anda bisa mengembalikan file secara langsung
    return send_from_directory(app.static_folder, 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    # Logika untuk menghasilkan robots.txt
    return """
    User-agent: *
    Disallow: /private/
    Disallow: /cgi-bin/
    Disallow: /images/
    Disallow: /pages/thankyou.html
    """
# Fungsi untuk menangani kesalahan 404
@app.errorhandler(404)
def page_not_found(error):
    # Cek apakah klien meminta JSON
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        # Jika klien meminta JSON, kirim respons dalam format JSON
        response = jsonify({'error': 'Not found'})
        response.status_code = 404
        return response
    # Jika tidak, kirim respons dalam format HTML
    return render_template('404.html'), 404

# Route untuk halaman yang tidak ada
@app.route('/invalid')
def invalid():
    # Menggunakan abort untuk memicu kesalahan 404
    abort(404)

from . import api_user, api_admin, login, proses_deteksi
