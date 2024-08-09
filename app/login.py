from . import app,db,bcrypt,jwt,Role,User,Profile,mail,s,login_role_required
from itsdangerous import BadSignature, SignatureExpired
import re
from flask import request,render_template,redirect,url_for,jsonify,session,flash,render_template_string
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,unset_jwt_cookies
from flask_mail import Message

@app.route('/tambah_admin')
def tambah():
    return render_template('admin/register.html')
        
# Endpoint untuk membuat token
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"msg": "Invalid request"}), 400

        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"msg": "username salah"}), 404
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"msg": "password salah"}), 401
        if user.verify_email == False:
            return jsonify({"msg": "username salah"}), 401
        user_roles = [role.name for role in user.roles]
        access_token = create_access_token(identity=username)
        session['jwt_token'] = access_token
        session['full_name'] = username
        session['id'] = user.id
        profile = Profile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = Profile(user_id=user.id, full_name='', address='', email='', phone_number='', bio='', nama_anak='', usia_anak=None)
            db.session.add(profile)
            db.session.commit()
        profile = Profile.query.filter_by(user_id=user.id).first()
        
        # Redirect berdasarkan peran user
        if 'admin' in user_roles:
            session['role'] = 'admin'
            print(session)
            return redirect(url_for('dashboard_admin'))
        elif 'user' in user_roles:
            session['role'] = 'user'
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
                return redirect(url_for('dashboard_user'))

    return render_template('user/login.html')
# Endpoint yang memerlukan autentikasi
def unset_session():
    response = jsonify({'message': 'Logout berhasil'})
    unset_jwt_cookies(response)
    session.pop('jwt_token', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('id', None)
    session.pop('full_name', None)
    session.pop('address', None)
    session.pop('email', None)
    session.pop('phone_number', None)
    session.pop('bio', None)
    session.pop('nama_anak', None)
    session.pop('usia_anak', None)
@app.route('/keluar')
def keluar():
    # Hapus token dari cookie (anda bisa menghapus token dari header juga jika tidak menggunakan cookie)
    unset_session()
    flash('Sukses Logout')
    return redirect(url_for('login'))

@jwt.expired_token_loader
def expired_token_callback():
    return redirect(url_for('login'))

@app.route('/bikin_akun_admin', methods=['GET', 'POST'])
@login_role_required('admin')
def register_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400
        
        # Check if the username and emaillegreop[d] already exists
        print(username+' | '+password+' | ')
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({"msg": "Username already  exists"}), 400
        email = User.query.filter_by(email=email).first()
        if email:
            return jsonify({"msg": "Email already  exists"}), 400

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # Create a new user
        new_user = User(username=username, password=hashed_password, verify_email=True)

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()
        
        new_user.roles.append(admin_role)
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successfull')
        return redirect(url_for('login', msg='Registration Successful'))

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
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    # Create a new user
    new_user = User(username=username, password=hashed_password, verify_email=False)
    admin_role = Role.query.filter_by(name='user').first()
    if not admin_role:
        admin_role = Role(name='user')
        db.session.add(admin_role)
        db.session.commit()
    
    new_user.roles.append(admin_role)
    
    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    
    profile = Profile(user_id=new_user.id, full_name='', address='', email=email, phone_number='', bio='', nama_anak='', usia_anak=None)
    db.session.add(profile)
    db.session.commit()

    token = s.dumps(email, salt='email-confirm')

    conf_email_url = url_for('confirm_email', token=token, _external=True)
    email_body = render_template_string('''
        Hello {{ username }},
        
        Anda menerima email ini, karena kami memerlukan verifikasi email untuk akun Anda agar aktif dan dapat digunakan.
        
        Silakan klik tautan di bawah ini untuk verifikasi email Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
        
        confirm youe email: {{ conf_email_url }}
        
        hubungi dukungan jika Anda memiliki pertanyaan.
        
        Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer zulfanisa0103@gmail.com .
        
        Salam Hangat,
        
        Pejuang D4
    ''', username=username,  conf_email_url=conf_email_url)

    msg = Message('Confirmasi Email Anda',
                  sender='zulfanisa0103@gmail.com', recipients=[email])

    msg.body = email_body
    mail.send(msg)

    flash(" Register berhasil silahkan cek email anda.")

    return redirect(url_for('login', msg='Register Berhasil silahkan cek email anda '))
@app.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({"message": "Token telah kedaluwarsa"}), 400
    except BadSignature:
        return jsonify({"message": "Token tidak valid"}), 400
    
    profile = Profile.query.filter_by(email=email).first()
    user = User.query.filter_by(id=profile.user_id).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Update the verify_email field to True
    user.verify_email = True
    db.session.commit()   
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

@app.route("/forgotpassword",methods=["GET","POST"])
def forgot_password():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"message": "Email harus diisi"}), 400
            
        profile = Profile.query.filter_by(email=email).first()
        user = User.query.filter_by(id=profile.user_id).first()

        if not user:
            return jsonify({"message": "Email tidak ditemukan"}), 404

        token = s.dumps(email, salt='reset-password')

        reset_password_url = url_for('', token=token, _external=True)
        email_body = render_template_string('''
            Hello {{ user["name"] }},
            
            Anda menerima email ini, karena kami menerima permintaan untuk mengatur ulang kata sandi akun Anda.
            
            Silakan klik tautan di bawah ini untuk mengatur ulang kata sandi Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
            
            Reset your password: {{ reset_password_url }}
            
            Jika Anda tidak meminta pengaturan ulang kata sandi, abaikan email ini atau hubungi dukungan jika Anda memiliki pertanyaan.
            
            Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer zulfanisa0103@gmail.com .
            
            Salam Hangat,
            
            Mriki_Project
        ''', user=user,  reset_password_url=reset_password_url)

        msg = Message('Reset Kata Sandi Anda',
                    sender='zulfanisa0103@gmail.com ', recipients=[email])

        msg.body = email_body
        mail.send(msg)


        return jsonify({"message": "Email untuk mereset kata sandi telah dikirim."}), 200
    else:
        return render_template("forgot_password.html")


@app.route('/reset_password/<token>', methods=['GET'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({"message": "Token telah kedaluwarsa"}), 400
    except BadSignature:
        return jsonify({"message": "Token tidak valid"}), 400
    
    profile = Profile.query.filter_by(email=email).first()
    user = User.query.filter_by(id=profile.user_id).first()
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # Update the verify_email field to True
    user.verify_email = True
    db.session.commit()   
    return render_template("reset_password.html").format(token)
