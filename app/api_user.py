from . import app,mysql,db,History,Rekomendasi,User,Profile
from flask import render_template, request, jsonify, redirect, url_for,session,g,abort
import pandas as pd
from PIL import Image
from io import BytesIO
import os,textwrap, locale, json, uuid, time,re
from datetime import datetime

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
    return render_template('user/dashboard.html')
#halaman homepage
@app.route('/user/profile')
def profile():
    return render_template('user/profile.html')
@app.route('/user/update_profile', methods=['POST'])
def update_profile():
    user = User.query.filter_by(id=session['id']).first()
    profile = Profile.query.filter_by(user_id=session['id']).first()

    new_username = request.form.get('username')
    new_full_name = request.form.get('full_name')
    new_address = request.form.get('address')
    new_email = request.form.get('email')
    new_phone_number = request.form.get('phone_number')
    new_bio = request.form.get('bio')
    new_nama_anak = request.form.get('nama_anak')
    new_usia_anak = request.form.get('usia_anak')

    if new_username:
        # Check if the new username is unique
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({"error": "Username already taken"}), 400
        user.username = new_username

    if new_full_name:
        profile.full_name = new_full_name

    profile.address = new_address
    profile.email = new_email
    profile.phone_number = new_phone_number
    profile.bio = new_bio
    profile.nama_anak = new_nama_anak
    profile.usia_anak = new_usia_anak

    db.session.commit()

#halaman hasil diagnosa
@app.route('/user/hasil_diagnosa/<id>')
def hasil_diagnosa(id):
    if 'username' not in session:
        abort(403)  # Forbidden, user tidak terautentikasi

    # Query data history berdasarkan id dan username dari session
    history_record = History.query.filter_by(nama_user=session['username'], id=id).first()
    if not history_record:
        abort(404)  # Not found, data history tidak ditemukan

    # Pastikan hasil_diagnosa adalah dictionary
    hasil_diagnosa_str = history_record.hasil_diagnosa

    # Mengganti kutipan tunggal dengan kutipan ganda
    hasil_diagnosa_str = re.sub(r"'", '"', hasil_diagnosa_str)
    print(hasil_diagnosa_str)
    try:
        hasil_diagnosa = json.loads(hasil_diagnosa_str)
    except json.JSONDecodeError as e:
        # Log error jika JSON tidak valid
        print(f"JSON Decode Error: {e}")
        hasil_diagnosa = {}

    # Query semua rekomendasi
    rekomendasi_records = Rekomendasi.query.all()
    print(rekomendasi_records)
    rekomendasi_list = [record.serialize() for record in rekomendasi_records]
    print(rekomendasi_list)

    # Gabungkan rekomendasi yang relevan dengan hasil diagnosa
    rekomendasi_diagnosa = {}
    for penyakit, jumlah in hasil_diagnosa.items():
        for rekomendasi in rekomendasi_list:
            if rekomendasi['nama'] == penyakit:
                rekomendasi_diagnosa[penyakit] = rekomendasi

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

@app.route('/ganti_password')
def ganti_password():

    return render_template('ganti_password.html')

@app.route('/gan')
def ganti_pasrd():

    return render_template('ganti_password.html')