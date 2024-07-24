from . import app,db,bcrypt,user_datastore,security,jwt,Role,User,Profile,mail,s
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import re
from flask import request,render_template,redirect,url_for,jsonify,session,flash,render_template_string
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,unset_jwt_cookies
from flask_mail import Message

@app.route('/login_admin')
def admin():
    return render_template('admin/login.html')
@app.route('/login_user')
def user():
    return render_template('user/login.html')
@app.route('/tambah_admin')
def tambah():
    return render_template('admin/register.html')
# Endpoint untuk membuat token
@app.route('/login_admin/proses', methods=['POST'])
def proses_admin():
    username = request.json['username']
    password = request.json['password']
    user = user_datastore.find_user(username=username)
    if user:
        if 'admin' in [role.name for role in user.roles]:
            if bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(identity=username)

                session['jwt_token'] = access_token
                session['role'] = "admin"
                session['full_name'] = username
                flash('Login Berhasil')
                return jsonify(access_token=access_token)
            else:
                return jsonify({"msg": "password salah"}), 401
        else:
            return jsonify({"msg": "User is not an admin"}), 403
    else:
        return jsonify({"msg": "username salah"}), 404
        
# Endpoint untuk membuat token
@app.route('/login_user/proses', methods=['POST'])
def proses_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Invalid request"}), 400

    username = data['username']
    password = data['password']
    user = user_datastore.find_user(username=username)
    if not user:
        return jsonify({"msg": "username salah"}), 404

    if 'user' not in [role.name for role in user.roles]:
        return jsonify({"msg": "User is not a regular user"}), 403

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "password salah"}), 401

    access_token = create_access_token(identity=username)
    session['jwt_token'] = access_token
    session['role'] = "user"
    session['full_name'] = username
    session['id'] = user.id
    profile = Profile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = Profile(user_id=user.id, full_name='', address='', email='', phone_number='', bio='', nama_anak='', usia_anak='')
        db.session.add(profile)
        db.session.commit()
    profile = Profile.query.filter_by(user_id=user.id).first()
    session['full_name'] = profile.full_name
    session['address'] = profile.address
    session['email'] = profile.email
    session['phone_number'] = profile.phone_number
    session['bio'] = profile.bio
    session['nama_anak'] = profile.nama_anak
    session['usia_anak'] = profile.usia_anak
    print(session)
    if profile.full_name == "" or profile.nama_anak == "" or profile.usia_anak == "" or profile.email == "" or profile.phone_number == "":
        return jsonify(access_token=access_token, redirect_url=url_for('profile'))
    else:
        return jsonify(access_token=access_token, redirect_url=url_for('dashboarduser'))

# Endpoint yang memerlukan autentikasi
def unset_session():
    response = jsonify({'message': 'Logout berhasil'})
    unset_jwt_cookies(response)
    session.pop('jwt_token', None)
    session.pop('username', None)
    session.pop('role', None)
@app.route('/keluar')
def keluar():
    # Hapus token dari cookie (anda bisa menghapus token dari header juga jika tidak menggunakan cookie)
    if session['role']=='admin':
        unset_session()
        flash('Sukses Logout')
        return redirect(url_for('admin'))
    elif session['role']=='user':
        unset_session()
        flash('Sukses Logout')
        return redirect(url_for('user'))
    else:
        unset_session()
        return redirect(url_for('index'))

@jwt.expired_token_loader
def expired_token_callback():
    return redirect(url_for('masuk'))

@app.route('/bikin_akun_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        jwt_required()
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400
        
        # Check if the username already exists
        print(username+' | '+password+' | ')
        if user_datastore.find_user(username=username):
            return jsonify({"msg": "Username already  exists"}), 400

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Check if the admin role exists, if not create it
        admin_role = user_datastore.find_role('admin')
        if not admin_role:
            admin_role = user_datastore.create_role(name='admin')
            db.session.commit()
            
        # Create a new user
        user = user_datastore.create_user(username=username, password=hashed_password, active=True)
        user_datastore.add_role_to_user(user, admin_role)
        db.session.commit()

        flash('Registration successfull')
        return redirect(url_for('login_admin', msg='Registration Successful'))

    return render_template('admin/register.html')

# Function to validate email format
def is_valid_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.match(regex, email)

@app.route('/bikin_akun_user', methods=['POST'])
def register_user():
    data = request.get_json()
    print(data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    re_password = data.get('re_password')

    if not username or not email or not password or not re_password:
        return jsonify({"msg": "All fields are required"}), 400

    if not is_valid_email(email):
        return jsonify({"msg": "Invalid email format"}), 400

    if password != re_password:
        return jsonify({"msg": "Passwords do not match"}), 400

    if user_datastore.find_user(username=username):
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    admin_role = user_datastore.find_role('user')
    if not admin_role:
        admin_role = user_datastore.create_role(name='user')
        db.session.commit()

    user = user_datastore.create_user(username=username, password=hashed_password, active=True)
    user_datastore.add_role_to_user(user, admin_role)
    db.session.commit()
    profile = Profile(user_id=user.id, full_name='', address='', email=email, phone_number='', bio='', nama_anak='', usia_anak='')
    db.session.add(profile)
    db.session.commit()

    token = s.dumps(email, salt='email-confirm')

    conf_email_url = url_for('confirm_email', token=token, _external=True)
    email_body = render_template_string('''
        Hello {{ username }},
        
        Anda menerima email ini, karena kami memerlukan verifikasi email untuk akun Anda agar aktif dan dapat digunakan.
        
        Silakan klik tautan di bawah ini untuk mengatur ulang kata sandi Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
        
        Reset your password: {{ conf_email_url }}
        
        hubungi dukungan jika Anda memiliki pertanyaan.
        
        Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer masteraldi2809@gmail.com.
        
        Salam Hangat,
        
        Pejuang D4
    ''', username=username,  conf_email_url=conf_email_url)

    msg = Message('Confirmasi Email Anda',
                  sender='@gmail.com', recipients=[email])

    msg.body = email_body
    mail.send(msg)

    flash("Email untuk mereset kata sandi telah dikirim.")

    return redirect(url_for('user'))
@app.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({"message": "Token telah kedaluwarsa"}), 400
    except BadSignature:
        return jsonify({"message": "Token tidak valid"}), 400
    
    user_datastore.update_one({"email": email}, {"$set": {"verify_email": True}})    
    return '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Email Verify</title>
      </head>
      <body>
        <h1>Email Telah Terverifikasi </h1>
      </body>
    </html>
    '''.format(token)

@app.post("/forgotpassword")
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email harus diisi"}), 400
    
    user = user_datastore.find_one({"email": email})

    if not user:
        return jsonify({"message": "Email tidak ditemukan"}), 404

    token = s.dumps(email, salt='email-confirm')

    reset_password_url = url_for('confirm_email', token=token, _external=True)
    email_body = render_template_string('''
        Hello {{ user["name"] }},
        
        Anda menerima email ini, karena kami menerima permintaan untuk mengatur ulang kata sandi akun Anda.
        
        Silakan klik tautan di bawah ini untuk mengatur ulang kata sandi Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
        
        Reset your password: {{ reset_password_url }}
        
        Jika Anda tidak meminta pengaturan ulang kata sandi, abaikan email ini atau hubungi dukungan jika Anda memiliki pertanyaan.
        
        Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer masteraldi2809@gmail.com.
        
        Salam Hangat,
        
        Mriki_Project
    ''', user=user,  reset_password_url=reset_password_url)

    msg = Message('Reset Kata Sandi Anda',
                  sender='masteraldi2809@gmail.com', recipients=[email])

    msg.body = email_body
    mail.send(msg)


    return jsonify({"message": "Email untuk mereset kata sandi telah dikirim."}), 200
