from . import app,db,bcrypt,user_datastore,security,jwt,Role,User,Profile
import re
from flask import request,render_template,redirect,url_for,jsonify,session,flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,unset_jwt_cookies
    
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
        print(email)
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
    flash('Registrasi Berhasil')
    return redirect(url_for('user', msg='Registration Successful'))
