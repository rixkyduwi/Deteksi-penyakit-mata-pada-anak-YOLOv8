from . import app,mysql,db,allowed_file, History,Rekomendasi,login_role_required
from flask import render_template, request, jsonify, redirect, url_for,session,g,abort
import os,textwrap, locale, json, uuid, time,re
import pandas as pd
from PIL import Image
from io import BytesIO
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.before_request
def before_request():
    g.con = mysql.connection.cursor()
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'con'):
        g.con.close()
        
def do_image(do, table, id):
    try:
        if do == "delete":
            filename = get_image_filename(table, id)
            delete_image(filename)
            return True
        file = request.files['gambar']
        if file is None or file.filename == '':
            return "default.jpg"
        else:
            filename = get_image_filename(table, id)
            delete_image(filename)
            return resize_and_save_image(file, table, id)
    except KeyError:
        if do == "edit":
            if table =="galeri":
                return True
            reset = request.form['reset']
            print(reset)
            if reset=="true":
                g.con.execute(f"UPDATE {table} SET gambar = %s WHERE id = %s", ("default.jpg", id))
                mysql.connection.commit()
        return "default.jpg"# Tangkap kesalahan jika kunci 'gambar' tidak ada dalam request.files
    except FileNotFoundError:
        pass  # atau return "File tidak ditemukan."
    except Exception as e:
        print(str(e))
        return str(e)

def resize_and_save_image(file, table=None, id=None):
    img = Image.open(file).convert('RGB').resize((600, 300))
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    random_name = uuid.uuid4().hex + ".jpg"
    destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    img.save(destination)
    if table and id:
        g.con.execute(f"UPDATE {table} SET gambar = %s WHERE id = %s", (random_name, id))
        mysql.connection.commit()
        return True
    else:
        return random_name
def get_image_filename(table, id):
    g.con.execute(f"SELECT gambar FROM {table} WHERE id = %s", (id,))
    result = g.con.fetchone()
    if result == "default.jpg":
        return None
    return result[0] if result else None

def delete_image(filename):
    if filename == "default.jpg":
        return True
    if filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(image_path):
            os.remove(image_path)
            
def fetch_data_and_format(query):
    g.con.execute(query)
    data = g.con.fetchall()
    column_names = [desc[0] for desc in g.con.description]
    info_list = [dict(zip(column_names, row)) for row in data]
    return info_list
            
#halaman admin
@app.route('/admin/dashboard')
@login_role_required('admin')
def dashboard():
    return render_template('admin/dashboard.html')
#halaman history konsultasi
@app.route('/admin/history_konsultasi')
@login_role_required('admin')
def history_konsultasi():
    histori_records = History.query.all()
    print(histori_records)
    return render_template('admin/history_konsultasi.html',histori_records= histori_records)
#halaman penyakit terbanyak
@app.route('/admin/penyakit_terbanyak')
@login_role_required('admin')
def penyakit_terbanyak():
    # Daftar nama penyakit
    names = ['strabismus (mata juling)', 'ptosis (kelopak mata turun)', 'mata merah', 'mata bengkak', 'mata bintitan']

    # Inisialisasi jumlah kasus dengan 0 untuk setiap nama
    jml_kasus = [0] * len(names)

    # Ambil data dari database
    history_records = History.query.all()

    # Hitung jumlah kasus untuk setiap penyakit
    for record in history_records:
        hasil_diagnosa = record.hasil_diagnosa  # Sesuaikan dengan struktur data Anda
        for index, penyakit in enumerate(names):
            if penyakit in hasil_diagnosa:  # Sesuaikan dengan cara Anda menyimpan data penyakit
                jml_kasus[index] += 1

    return render_template('admin/penyakit_terbanyak.html', names=names, jml_kasus=jml_kasus)
# Setelah proses penghitungan selesai, data dihitung kemudian dikirim ke template HTML penyakit_terbanyak.html menggunakan fungsi render_template.
# Template HTML akan menerima dua variabel: names dan jml_kasus, yang kemudian dapat digunakan untuk menampilkan data di halaman web.

#halaman hasil diagnosa
@app.route('/admin/history_konsultasi/<id>')
@login_role_required('admin')
def admin_hasil_diagnosa(id):
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