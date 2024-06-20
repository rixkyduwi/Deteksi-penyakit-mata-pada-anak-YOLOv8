from . import app,mysql,db,allowed_file
from flask import render_template, request, jsonify, redirect, url_for,session,g
import os,textwrap, locale, json, uuid, time
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
def dashboard():
    return render_template('admin/dashboard.html')
#halaman history konsultasi
@app.route('/admin/history_konsultasi')
def history_konsultasi():
    return render_template('admin/history_konsultasi.html')
#halaman penyakit terbanyak
@app.route('/admin/penyakit_terbanyak')
def penyakit_terbanyak():
    return render_template('admin/penyakit_terbanyak.html')
#sejarah
@app.route('/admin/infodesa')
def admininfodesa():
    info_list = fetch_data_and_format("SELECT * FROM sejarah_desa")
    return render_template("admin/infodesa.html", info_list = info_list)

#berita
@app.route('/admin/berita')
def admindberita():
    info_list=fetch_data_and_format("SELECT * FROM berita order by id DESC")
    return render_template("admin/berita.html", info_list = info_list)

@app.route('/admin/tambah_berita', methods=['POST'])
@jwt_required()
def tambah_berita():
    judul = request.form['judul']
    link = '_'.join(filter(None, [judul.replace("#", "").replace("?", "").replace("/", "").replace(" ", "_")]))
    deskripsi = request.form['deskripsi']
    deskripsi = textwrap.shorten(deskripsi, width=75, placeholder="...")
    deskripsifull = request.form['deskripsifull']
    try: 
        random_name = do_image("tambah","berita","")
        g.con.execute("INSERT INTO berita (judul, gambar , deskripsi, deskripsifull, link ) VALUES (%s,%s,%s,%s,%s)",(judul,random_name,deskripsi,deskripsifull,link))
        mysql.connection.commit()
        return jsonify({"msg":"SUKSES"})
    except Exception as e:
        str(e)
        return jsonify({"error": str(e)})
@app.route('/admin/edit_berita', methods=['PUT'])
@jwt_required()
def berita_edit():
    id = request.form['id']
    judul = request.form['judul']
    link = '_'.join(filter(None, [judul.replace("#", "").replace("?", "").replace("/", "").replace(" ", "_")]))
    deskripsi = request.form['deskripsi']
    deskripsi = textwrap.shorten(deskripsi, width=75, placeholder="...")
    deskripsifull = request.form['deskripsifull']
    try:
        status = do_image("edit","berita",id)
        g.con.execute("UPDATE berita SET judul = %s, deskripsi = %s, deskripsifull = %s, link = %s  WHERE id = %s",(judul,deskripsi,deskripsifull,link,id))
        mysql.connection.commit()
        return jsonify({"msg" : "SUKSES"})
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)})

@app.route('/hapus_berita', methods=['DELETE'])
@jwt_required()
def hapus_berita():
    id = request.form['id']
    try:
        do_image("delete","berita",id)
        g.con.execute("DELETE FROM berita WHERE id = %s", (id,))
        mysql.connection.commit()
        return jsonify({"msg": "SUKSES"})
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)})