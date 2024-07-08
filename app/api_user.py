from . import app,mysql,db,History,Rekomendasi,User,Profile,user_datastore,bcrypt
from flask import render_template, request, jsonify, redirect, url_for,session,g,abort
import pandas as pd
from PIL import Image
from io import BytesIO
import os,textwrap, locale, json, uuid, time,re
from datetime import datetime
from sqlalchemy.exc import IntegrityError

@app.before_request
def before_request():
    g.con = mysql.connection.cursor()
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'con'):
        g.con.close()
        
def fetch_data_and_format(query):
    g.con.execute(query)
    data = g.con.fetchall()
    column_names = [desc[0] for desc in g.con.description]
    info_list = [dict(zip(column_names, row)) for row in data]
    return info_list
def fetch_years(query):
    g.con.execute(query)
    data_thn = g.con.fetchall()
    thn = [{'tahun': str(sistem[0])} for sistem in data_thn]
    return thn
#halaman homepage
@app.route('/')
def index():
    return render_template('index.html')
#halaman tips
@app.route('/tips')
def userberita():
    # tips = fetch_data_and_format("SELECT * FROM tips order by id DESC")
    return render_template('tips.html')
@app.route('/tips/<link>')
def detail_berita(link):
    query = "SELECT * FROM berita where link = '"+ str(link) +"' order by id DESC "
    berita = fetch_data_and_format(query)
    return render_template('detail_berita.html',info_list = berita)
#halaman dashboard user
@app.route('/user/dashboard')
def dashboarduser():
    if not all([session.get('full_name'), session.get('nama_anak'), session.get('usia_anak'), session.get('email'), session.get('phone_number')]):
        return redirect(url_for("profile"))
    else:
        return render_template('user/dashboard.html')
#halaman homepage
@app.route('/user/profile')
def profile():
    return render_template('user/profile.html')
@app.route('/user/update_profile', methods=['POST'])
def update_profile():
    user = User.query.filter_by(id=session['id']).first()
    profile = Profile.query.filter_by(user_id=session['id']).first()

    new_full_name = request.form.get('full_name')
    new_address = request.form.get('address')
    new_email = request.form.get('email')
    new_phone_number = request.form.get('phone_number')
    new_bio = request.form.get('bio')
    new_nama_anak = request.form.get('nama_anak')
    new_usia_anak = request.form.get('usia_anak')
    print(new_email)
    print(new_full_name)
    print(new_phone_number)
    print(new_nama_anak)
    print(new_usia_anak)

    try:
        if new_full_name:
            # Check if the new username is unique
            existing_user = User.query.filter_by(username=new_full_name).first()

            # Check if the new username is the same as the current username
            if new_full_name == session['full_name']:
                user.username = new_full_name
            elif existing_user and existing_user.id != user.id:
                return jsonify({"msg": "Username already taken"})
            else:
                user.username = new_full_name
                profile.full_name = new_full_name

        profile.address = new_address
        profile.email = new_email
        profile.phone_number = new_phone_number
        profile.bio = new_bio
        profile.nama_anak = new_nama_anak
        profile.usia_anak = new_usia_anak

        db.session.commit()

        # Update session with new data
        session['full_name'] = profile.full_name
        session['address'] = profile.address
        session['email'] = profile.email
        session['phone_number'] = profile.phone_number
        session['bio'] = profile.bio
        session['nama_anak'] = profile.nama_anak
        session['usia_anak'] = profile.usia_anak

        # Check if all required fields are filled
        if not all([user.username, profile.full_name, profile.nama_anak, profile.usia_anak, profile.email, profile.phone_number]):
            return jsonify({"msg": "Silakan lengkapi semua data dahulu sebelum bisa mengakses fitur-fitur kami"})

        return jsonify({"msg": "Profil berhasil diperbarui"})

    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e.orig)  # Extract the original error message
        return jsonify({"msg": f"Error: {error_message}"}), 400
    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        return jsonify({"msg": f"Error: {error_message}"}), 400

@app.route('/ganti_password')
def ganti_password():

    return render_template('ganti_password.html')

@app.route('/ganti_password', methods=["POST"])
def ganti_password_post():
    # Coba ambil data dari JSON
    data = request.get_json()
    if data:
        password_lama = data.get('password_lama')
        password_baru = data.get('password_baru')
    else:
        # Jika tidak ada data JSON, ambil dari form
        password_lama = request.form.get('password_lama')
        password_baru = request.form.get('password_baru')
    user = user_datastore.find_user(username=session['full_name'])
    
    if user:
        if 'admin' in [role.name for role in user.roles]:
            if bcrypt.check_password_hash(user.password, password_lama):
                # Mengganti password lama dengan password baru
                user.password = bcrypt.generate_password_hash(password_baru).decode('utf-8')
                user_datastore.put(user)
                db.session.commit()
                return jsonify({"msg": "SUKSES"})
            else:
                return jsonify({"msg": "Password lama salah"})
        else:
            return jsonify({"msg": "Akses ditolak"})
    else:
        return jsonify({"msg": "user tidak ditemukan"})

