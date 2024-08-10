from . import app,mysql,db,History,Rekomendasi,User,Profile,bcrypt,login_role_required, DataAnak
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
def detail_tips(link):
    query = "SELECT * FROM berita where link = '"+ str(link) +"' order by id DESC "
    berita = fetch_data_and_format(query)
    return render_template('detail_berita.html',info_list = berita)
#halaman dashboard user
@app.route('/user/dashboard')
@login_role_required('user')
def dashboarduser():
    if not all([session.get('full_name'), session.get('nama_anak'), session.get('usia_anak'), session.get('email')]):
        return redirect(url_for("profile"))
    else:
        return render_template('user/dashboard.html')
#halaman crud data anak
@app.route('/user/data_anak', methods=['POST'])
@login_role_required('user')
def create_data_anak():
    nama_anak = request.form.get('nama_anak')
    usia_anak = request.form.get('usia_anak')
    jenis_kelamin = request.form.get('jenis_kelamin')

    try:
        data_anak = Data_Anak(
            user_id=session['id'],
            nama_anak=nama_anak,
            usia_anak=int(usia_anak),
            jenis_kelamin=jenis_kelamin
        )
        db.session.add(data_anak)
        db.session.commit()

        return jsonify({"msg": "Data anak berhasil ditambahkan"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 400
@app.route('/user/data_anak/<int:id>', methods=['POST'])
@login_role_required('user')
def update_data_anak(id):
    try:
        data_anak = Data_Anak.query.filter_by(id=id, user_id=session['id']).first()

        if not data_anak:
            return jsonify({"msg": "Data anak tidak ditemukan"}), 404

        nama_anak = request.form.get('nama_anak')
        usia_anak = request.form.get('usia_anak')
        jenis_kelamin = request.form.get('jenis_kelamin')

        data_anak.nama_anak = nama_anak
        data_anak.usia_anak = int(usia_anak)
        data_anak.jenis_kelamin = jenis_kelamin

        db.session.commit()

        return jsonify({"msg": "Data anak berhasil diperbarui"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 400
@app.route('/user/data_anak/<int:id>', methods=['DELETE'])
@login_role_required('user')
def delete_data_anak(id):
    try:
        data_anak = Data_Anak.query.filter_by(id=id, user_id=session['id']).first()

        if not data_anak:
            return jsonify({"msg": "Data anak tidak ditemukan"}), 404

        db.session.delete(data_anak)
        db.session.commit()

        return jsonify({"msg": "Data anak berhasil dihapus"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 400

#halaman profile
@app.route('/user/profile')
@login_role_required('user')
def profile():
    anak_anak = Data_Anak.query.filter_by(user_id=session['id']).all()
    data = [{"id": anak.id, "nama_anak": anak.nama_anak, "usia_anak": anak.usia_anak, "jenis_kelamin": anak.jenis_kelamin} for anak in anak_anak]
    return render_template('user/profile.html',data=data)

from sqlalchemy.exc import IntegrityError

@app.route('/user/update_profile', methods=['POST'])
@login_role_required('user')
def update_profile():
    user = User.query.filter_by(id=session['id']).first()
    profile = Profile.query.filter_by(user_id=session['id']).first()

    new_full_name = request.form.get('full_name')
    new_address = request.form.get('address')
    new_email = request.form.get('email')
    new_bio = request.form.get('bio')

    try:
        # Update profile fields only if they are provided and different from current values
        if new_full_name and new_full_name != profile.full_name:
            if User.query.filter(User.username == new_full_name, User.id != user.id).first():
                return jsonify({"msg": "Username already taken"}), 400
            profile.full_name = new_full_name

        if new_email and new_email != profile.email:
            if Profile.query.filter(Profile.email == new_email, Profile.user_id != user.id).first():
                return jsonify({"msg": "Email already taken"}), 400
            profile.email = new_email

        if new_address and new_address != profile.address:
            profile.address = new_address

        if new_bio and new_bio != profile.bio:
            profile.bio = new_bio

        db.session.commit()

        # Update session with new data
        session['full_name'] = profile.full_name
        session['address'] = profile.address
        session['email'] = profile.email
        session['bio'] = profile.bio

        # Check if all required fields are filled
        if not all([user.username, profile.full_name, profile.email]):
            return jsonify({"msg": "Silakan lengkapi semua data dahulu sebelum bisa mengakses fitur-fitur kami"}), 400

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
@login_role_required('user')
def ganti_password():
    return render_template('ganti_password.html')

@app.route('/ganti_password', methods=["POST"])
@login_role_required('user')
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
    user = User.query.filter_by(username=session['full_name']).first()
    if user:
        if bcrypt.check_password_hash(user.password, password_lama):
            # Mengganti password lama dengan password baru
            user.password = bcrypt.generate_password_hash(password_baru).decode('utf-8')
            db.session.commit()
            return jsonify({"msg": "SUKSES"})
        else:
            return jsonify({"msg": "Password lama salah"})
    else:
        return jsonify({"msg": "user tidak ditemukan"})

@app.route('/user/hasil_diagnosa/<id>')
@login_role_required('user')
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