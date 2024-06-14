from . import app,db,bcrypt,user_datastore,security,jwt,Role,User
from flask import request,render_template,redirect,url_for,jsonify,session,flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,unset_jwt_cookies
    
@app.route('/login_admin')
def admin():
    return render_template('admin/admin.html')
@app.route('/login_user')
def user():
    return render_template('admin/admin.html')

# Endpoint untuk membuat token
@app.route('/login_admin/proses', methods=['POST'])
def proses_admin():
        username = request.json['username']
        password = request.json['password']

        # Seharusnya Anda memverifikasi kredensial pengguna di sini
        # Misalnya, memeriksa username dan password di database
        if user:
            if 'admin' in [role.name for role in user.roles]:
                if bcrypt.check_password_hash(user.password, password):
                    access_token = create_access_token(identity=username)
                    session['jwt_token'] = access_token
                    session['username'] = username
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
        username = request.json['username']
        password = request.json['password']

        # Seharusnya Anda memverifikasi kredensial pengguna di sini
        # Misalnya, memeriksa username dan password di database
        if user:
            if 'user' in [role.name for role in user.roles]:
                if bcrypt.check_password_hash(user.password, password):
                    access_token = create_access_token(identity=username)
                    session['jwt_token'] = access_token
                    session['username'] = username
                    return jsonify(access_token=access_token)
                else:
                    return jsonify({"msg": "password salah"}), 401
            else:
                return jsonify({"msg": "User is not an admin"}), 403
        else:
            return jsonify({"msg": "username salah"}), 404

# Endpoint yang memerlukan autentikasi
@app.route('/keluar')
def keluar():
    # Hapus token dari cookie (anda bisa menghapus token dari header juga jika tidak menggunakan cookie)
    response = jsonify({'message': 'Logout berhasil'})
    unset_jwt_cookies(response)
    session.pop('jwt_token', None)
    session.pop('username', None)
    flash('Sukses Logout')
    return redirect(url_for('masuk'))

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

        #logout
        response = jsonify({'message': 'Logout berhasil'})
        unset_jwt_cookies(response)
        session.pop('jwt_token', None)
        session.pop('username', None)
        flash('Sukses Logout')
        return redirect(url_for('login_admin', msg='Registration Successful'))

    return render_template('admin/register.html')

@app.route('/bikin_akun_user', methods=['POST'])
def register_user():
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
    admin_role = user_datastore.find_role('user')
    if not admin_role:
        admin_role = user_datastore.create_role(name='user')
        db.session.commit()

    # Create a new user
    user = user_datastore.create_user(username=username, password=hashed_password, active=True)
    user_datastore.add_role_to_user(user, admin_role)
    db.session.commit()

    #logout
    response = jsonify({'message': 'Logout berhasil'})
    unset_jwt_cookies(response)
    session.pop('jwt_token', None)
    session.pop('username', None)
    flash('Sukses Logout')
    return redirect(url_for('login_user', msg='Registration Successful'))
