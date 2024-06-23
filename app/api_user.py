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

    try:
        hasil_diagnosa = json.loads(hasil_diagnosa_str)
    except json.JSONDecodeError as e:
        # Log error jika JSON tidak valid
        print(f"JSON Decode Error: {e}")
        hasil_diagnosa = {}

    # Query semua rekomendasi
    rekomendasi_records = Rekomendasi.query.all()
    rekomendasi_list = [record.serialize() for record in rekomendasi_records]

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

    return render_template('user/hasil_diagnosa.html', diagnosa=diagnosa)
#halaman homepage
@app.route('/ganti_password')
def ganti_password():
    return render_template('ganti_password.html')
#halaman profile
@app.route('/sejarah')
def sejarah():
    g.con.execute("SELECT * FROM sejarah_desa")
    sejarah = g.con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'sejarah': str(sistem[1])
        }
        info_list.append(list_data)
    return render_template("sejarah.html", info_list = info_list)

#halaman vidio
@app.route('/video')
def vidio():
    g.con.execute("SELECT * FROM vidio order by id DESC")
    berita = g.con.fetchall()
    info_list = []
    for sistem in berita:
        list_data = {
            'id': str(sistem[0]),
            'vidio': str(sistem[1])        
        }
        info_list.append(list_data)
    return render_template("video.html", info_list = info_list)

#halaman visi misi
@app.route('/visi_misi')
def visi_misi():
    g.con.execute("SELECT * FROM sejarah_desa")
    sejarah = g.con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'visi': str(sistem[2]),
            'misi': sistem[3],
        }
        info_list.append(list_data)
    return render_template("visimisi.html", info_list = info_list)

#halaman pemerintahan
@app.route('/pemerintahan_desa')
def pemerintahan_desa():
    g.con.execute("SELECT * FROM anggota order by id")
    anggota = g.con.fetchall()
    column_names = [desc[0] for desc in g.con.description]
    info_list = [dict(zip(column_names, row)) for row in anggota]
    return render_template("pemerintahan_desa.html", info_list = info_list)

#halaman badan desa
@app.route('/badan_desa')
def badan_desa():
    return jsonify({"msg":"under maintance"}),404

#halaman dana
@app.route('/dana/<thn>')
def dana_desa(thn):
    info_list = fetch_data_and_format("SELECT * FROM realisasi_pendapatan where tahun = "+thn+" ORDER BY id")
    info_list2 = fetch_data_and_format("SELECT * FROM realisasi_belanja where tahun = "+thn+" ORDER BY id")
    info_list3 = fetch_data_and_format("SELECT * FROM realisasi_pembiayaan where tahun = "+thn+" ORDER BY id")
    return render_template("dana.html", info_list=info_list, info_list2=info_list2, info_list3=info_list3, tahun=thn)
#halaman monografi
@app.route('/monografi')
def mono():
    g.con.execute("SELECT * FROM monografi")
    mono = g.con.fetchall()
    column_names = [desc[0] for desc in g.con.description]
    info_list = [dict(zip(column_names, row)) for row in mono]
    return render_template("user_data_desa/monografi.html", info_list = info_list)
#Halaman geografi
@app.route('/geografi')
def geo():
    g.con.execute("SELECT * FROM wilayah")
    wilayah = g.con.fetchall()
    column_names = [desc[0] for desc in g.con.description]
    info_list = [dict(zip(column_names, row)) for row in wilayah]
    return render_template("user_data_desa/geografi.html", info_list=info_list )

#halaman user galeri
@app.route('/galeri')
def galeri():
    g.con.execute("SELECT * FROM galeri order by id DESC")
    berita = g.con.fetchall()
    info_list = []
    for sistem in berita:
        list_data = {
            'id': str(sistem[0]),
            'judul': str(sistem[1]),
            'gambar': str(sistem[2]),
            'tanggal': str(sistem[3])
        }
        info_list.append(list_data)
    return render_template("/galeri.html", info_list = info_list)
#halaman user galeri
@app.route('/agenda')
def agenda():
    list_agenda=fetch_data_and_format("SELECT * FROM agenda")
    return render_template('agenda.html',list_agenda=list_agenda) 
#get info
@app.route('/info', methods=['GET'])
def get_info():
    g.con.execute("SELECT * FROM sejarah_desa")
    sejarah = g.con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'sejarah': str(sistem[1]),
            'visi': str(sistem[2]),
            'misi': str(sistem[3])
        }
        info_list.append(list_data)
    return jsonify(info_list)

#get fasilitas
@app.route('/fasilitas', methods=['GET'])
def get_fasilitas():
    g.con.execute("SELECT * FROM fasilitas")
    sejarah = g.con.fetchall()
    info_list = []
    for sistem in sejarah:
        list_data = {
            'id': str(sistem[0]),
            'fasilitas': str(sistem[1]),
            'kondisi': str(sistem[2])
        }
        info_list.append(list_data)
    return jsonify(info_list)

#get
@app.route('/surat', methods=['GET'])
def get_surat():
    g.con.execute("SELECT * FROM surat")
    surat = g.con.fetchall()
    info_list = []
    for sistem in surat:
        list_data = {
            'id': str(sistem[0]),
            'nama': str(sistem[1]),
            'hp': str(sistem[2]),
            'keterangan': str(sistem[3])
        }
        info_list.append(list_data)
    return jsonify(info_list)

@app.route('/tambah_surat', methods=['POST'])
def tambah_surat():
    nama = request.form['nama']
    hp = request.form['hp']
    keterangan = request.form['keterangan']
    g.con.execute("INSERT INTO surat (nama , hp, keterangan) VALUES (%s,%s,%s)",(nama,hp,keterangan))
    mysql.connection.commit()
    return jsonify({"msg":"SUKSES"})

@app.route('/edit_surat', methods=['POST'])
def edit_surat():
    id = request.form['id']
    nama = request.form['nama']
    hp = request.form['hp']
    keterangan = request.form['keterangan']
    g.con.execute("UPDATE surat SET nama = %s, hp = %s, keterangan = %s WHERE id = %s",(nama,hp,keterangan,id))
    mysql.connection.commit()
    return jsonify({"msg":"SUKSES"})

@app.route('/hapus_surat', methods=['POST'])
def hapus_surat():
    id = request.form['id']
    g.con.execute("DELETE FROM surat WHERE id = %s",(id))
    mysql.connection.commit()
    return jsonify({"msg":"SUKSES"})
#halaman bpd
@app.route('/bpd')
def bpd():
    g.con.execute("SELECT nama_jabatan FROM urutan_jabatan")
    rows = g.con.fetchall()
    urutan_jabatan = [row[0] for row in rows]
    list_info = fetch_data_and_format("SELECT * FROM bpd")
    sorted_list_info = sorted(list_info, key=lambda x: urutan_jabatan.index(x['jabatan']) if x['jabatan'] in urutan_jabatan else len(urutan_jabatan))
    return render_template('bpd.html', list_info=sorted_list_info)