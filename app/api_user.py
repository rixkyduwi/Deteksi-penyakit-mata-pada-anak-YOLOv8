from . import app,mysql,db
from flask import render_template, request, jsonify, redirect, url_for,session,g
import pandas as pd
from PIL import Image
from io import BytesIO
import os,textwrap, locale, json, uuid, time
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
def homepahe():
    thn_dana_list =fetch_data_and_format("SELECT tahun FROM realisasi_pendapatan group by tahun")
    session['list_thn_dana']= thn_dana_list 
    return render_template('index.html')
@app.route('/news')
def userberita():
    berita = fetch_data_and_format("SELECT * FROM berita order by id DESC")
    return render_template('homepage.html',info_list = berita)
#halaman berita
@app.route('/berita/<link>')
def detail_berita(link):
    query = "SELECT * FROM berita where link = '"+ str(link) +"' order by id DESC "
    berita = fetch_data_and_format(query)
    return render_template('detail_berita.html',info_list = berita)
#halaman sejarah
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