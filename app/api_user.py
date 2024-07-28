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
    if not all([session.get('full_name'), session.get('nama_anak'), session.get('usia_anak'), session.get('email')]):
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
    new_bio = request.form.get('bio')
    new_nama_anak = request.form.get('nama_anak')
    new_usia_anak = request.form.get('usia_anak')
    print(new_email)
    print(new_full_name)
    print(new_nama_anak)
    print(new_usia_anak)
# melihat nama profil di icon profil
    try:
        if new_full_name:
            # Check if the new username is unique
            existing_user = User.query.filter_by(username=new_full_name).first()

            # Check if the new username is the same as the current username
            if new_full_name == session['full_name']:
                profile.full_name = new_full_name
            elif existing_user and existing_user.id != user.id:
                return jsonify({"msg": "Username already taken"})
            else:
                profile.full_name = new_full_name

        profile.address = new_address
        profile.email = new_email
        profile.bio = new_bio
        profile.nama_anak = new_nama_anak
        profile.usia_anak = new_usia_anak

        db.session.commit()

        # Update session with new data
        session['full_name'] = profile.full_name
        session['address'] = profile.address
        session['email'] = profile.email
        session['bio'] = profile.bio
        session['nama_anak'] = profile.nama_anak
        session['usia_anak'] = profile.usia_anak

        # Check if all required fields are filled
        if not all([user.username, profile.full_name, profile.nama_anak, profile.usia_anak, profile.email]):
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
        if bcrypt.check_password_hash(user.password, password_lama):
            # Mengganti password lama dengan password baru
            user.password = bcrypt.generate_password_hash(password_baru).decode('utf-8')
            user_datastore.put(user)
            db.session.commit()
            return jsonify({"msg": "SUKSES"})
        else:
            return jsonify({"msg": "Password lama salah"})
    else:
        return jsonify({"msg": "user tidak ditemukan"})

@app.route('/user/hasil_diagnosa/<id>')
def user_hasil_diagnosa(id):
    if 'full_name' not in session:
        abort(403)  # Forbidden, user tidak terautentikasi

    # Query data history berdasarkan id dan username dari session
    history_record = History.query.filter_by(id=id).first()
    if not history_record:
        abort(404)  # Not found, data history tidak ditemukan
    
    # Pastikan hasil_diagnosa adalah dictionary
    hasil_diagnosa_str = history_record.hasil_diagnosa

    hasil_diagnosa = hasil_diagnosa_str.split(",")

    if hasil_diagnosa[-1] == '':
        hasil_diagnosa.pop()
    print(hasil_diagnosa)
    # Query semua rekomendasi
    rekomendasi_records = Rekomendasi.query.all()
    print(rekomendasi_records)
    rekomendasi_list = [record.serialize() for record in rekomendasi_records]
    print(rekomendasi_list)

    # Gabungkan rekomendasi yang relevan dengan hasil diagnosa
    rekomendasi_diagnosa = {}
    for penyakit in hasil_diagnosa:
        for rekomendasi in rekomendasi_list:
            if rekomendasi['nama'] == penyakit:
                rekomendasi_diagnosa[penyakit] = rekomendasi
                print(rekomendasi['link_rekomendasi'])
                link_rekomendasi = rekomendasi['link_rekomendasi']
                link_rekomendasi = link_rekomendasi.split(",")
                rekomendasi_diagnosa[penyakit]['link_rekomendasi'] = link_rekomendasi
    print(rekomendasi_diagnosa)
    diagnosa = {
        'nama_user': history_record.nama_user,
        'nama_anak': history_record.nama_anak,
        'usia_anak': history_record.usia_anak,
        'tanggal_konsultasi': history_record.tanggal_konsultasi,
        'file_deteksi': history_record.file_deteksi,
        'hasil_diagnosa': hasil_diagnosa,
        'rekomendasi_diagnosa': rekomendasi_diagnosa,
    }
    print(diagnosa)

    return render_template('user/hasil_diagnosa.html', diagnosa=diagnosa)