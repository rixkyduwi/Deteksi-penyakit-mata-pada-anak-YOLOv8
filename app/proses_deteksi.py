import os
import uuid
import torch
import datetime
import subprocess
import json
from flask import Flask, jsonify, request, session
from . import app,db,History
from PIL import Image
from io import BytesIO
# Load the model
project_directory = os.path.abspath(os.path.dirname(__file__))
model_path = os.path.join(project_directory, 'best.pt')
model = torch.load(model_path)
# Check the model's attributes to determine the version
model_info = {
    "class_name": model.__class__.__name__,
    "model_details": model
}

import ultralytics
ultralytics.checks()
@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['gambar']
    if file is None or file.filename == '':
        return "error"
    # Image.open(file): Membuka gambar dari file.
# .convert('RGB'): Mengubah gambar menjadi format RGB.
# .resize((600, 300)): Mengubah ukuran gambar menjadi 600x300 piksel.
# img_io = BytesIO(): Membuat objek BytesIO untuk menyimpan gambar dalam memori.
# img.save(img_io, 'JPEG', quality=70): Menyimpan gambar ke objek BytesIO dalam format JPEG dengan kualitas 70%.
# img_io.seek(0): Mengatur posisi pembacaan objek BytesIO ke awal.
    img = Image.open(file).convert('RGB').resize((600, 300))
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    random_name = uuid.uuid4().hex + ".jpg"
    destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    img.save(destination)

    save_path = app.config['DETECT_FOLDER']
    conf = 0.55

    print("loading..")
    command = [
        'yolo',
        'task=detect',
        'mode=predict',
        f'model={model_path}',
        f'conf={conf}',
        f'source={destination}',
        f'project={save_path}',
        'save=True'
    ]

    try:
        # Menjalankan perintah shell
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
        output = result.stdout

        # Logging untuk output proses
        print(f"Command output: {output}")

        # Mengecek kemunculan setiap nama dalam output
        names = ['strabismus (mata juling)', 'ptosis (kelopak mata turun)', 'mata merah', 'mata bengkak', 'mata bintitan']
        found_names = ""
        for name in names:
            if name in output:
                found_names += name + ","
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Cari folder predict terbaru di dalam save_path
        subfolders = [f.path for f in os.scandir(save_path) if f.is_dir()]
        latest_folder = max(subfolders, key=os.path.getmtime)  # Folder terbaru berdasarkan waktu modifikasi
        latest_folder = latest_folder.replace("./app/static/detect\\", "")
        detected_file_path = latest_folder+"/"+random_name
        print(detected_file_path)
        # Menampilkan hasil
        if found_names != "":
            print("Found names and their counts in output:")
            print(found_names)
            history = History(
                nama_user=session['full_name'],
                nama_anak=session['nama_anak'],
                usia_anak=session['usia_anak'],
                tanggal_konsultasi=current_time,
                file_deteksi=detected_file_path,
                hasil_diagnosa=found_names
            )
            db.session.add(history)
            db.session.commit()

            new_history_id = history.id
            return jsonify({"msg": "SUKSES", "id_hasil": new_history_id})
        else:
            history = History(
                nama_user=session['full_name'],
                nama_anak=session['nama_anak'],
                usia_anak=session['usia_anak'],
                tanggal_konsultasi=current_time,
                file_deteksi=detected_file_path,
                hasil_diagnosa="sehat"
            )
            db.session.add(history)
            db.session.commit()
            new_history_id = history.id
            print("None of the names were found in the output.")
            return jsonify({"msg": "SUKSES", "id_hasil": new_history_id})

    except subprocess.CalledProcessError as e:
        return jsonify({'msg': e.stderr}), 500
    
from facenet_pytorch import MTCNN
mtcnn = MTCNN(keep_all=False, device='cuda' if torch.cuda.is_available() else 'cpu')
@app.route('/predict_mtcnn', methods=['POST'])
def predict_mtcnn():
    file = request.files['gambar']
    if file is None or file.filename == '':
        return "error"
    img = Image.open(file).convert('RGB').resize((600, 300))
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    random_name = uuid.uuid4().hex + ".jpg"
    destination = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    img.save(destination)

    save_path = app.config['DETECT_FOLDER']
    conf = 0.55

    print("loading..")
    boxes, _ = mtcnn.detect(img)
    if boxes is not None:
        command = [
        'yolo',
        'task=detect',
        'mode=predict',
        f'model={model_path}',
        f'conf={conf}',
        f'source={destination}',
        f'project={save_path}',
        'save=True'
        ]

        try:
            # Menjalankan perintah shell
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
            output = result.stdout

            # Logging untuk output proses
            print(f"Command output: {output}")

            # Mengecek kemunculan setiap nama dalam output
            names = ['strabismus (mata juling)', 'ptosis (kelopak mata turun)', 'mata merah', 'mata bengkak', 'mata bintitan']
            found_names = ""
            for name in names:
                if name in output:
                    found_names += name + ","
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Cari folder predict terbaru di dalam save_path
            subfolders = [f.path for f in os.scandir(save_path) if f.is_dir()]
            latest_folder = max(subfolders, key=os.path.getmtime)  # Folder terbaru berdasarkan waktu modifikasi
            latest_folder = latest_folder.replace("./app/static/detect\\", "")
            detected_file_path = latest_folder+"/"+random_name
            print(detected_file_path)
            # Menampilkan hasil
            if found_names != "":
                print("Found names and their counts in output:")
                print(found_names)
                history = History(
                    nama_user=session['full_name'],
                    nama_anak=session['nama_anak'],
                    usia_anak=session['usia_anak'],
                    tanggal_konsultasi=current_time,
                    file_deteksi=detected_file_path,
                    hasil_diagnosa=found_names
                )
                db.session.add(history)
                db.session.commit()

                new_history_id = history.id
                return jsonify({"msg": "SUKSES", "id_hasil": new_history_id})
            else:
                history = History(
                    nama_user=session['full_name'],
                    nama_anak=session['nama_anak'],
                    usia_anak=session['usia_anak'],
                    tanggal_konsultasi=current_time,
                    file_deteksi=detected_file_path,
                    hasil_diagnosa="sehat"
                )
                db.session.add(history)
                db.session.commit()
                new_history_id = history.id
                print("None of the names were found in the output.")
                return jsonify({"msg": "SUKSES", "id_hasil": new_history_id})

        except subprocess.CalledProcessError as e:
            return jsonify({'msg': e.stderr}), 500
    else:
        history = History(
            nama_user=session['full_name'],
            nama_anak=session['nama_anak'],
            usia_anak=session['usia_anak'],
            tanggal_konsultasi=current_time,
            file_deteksi=detected_file_path,
            hasil_diagnosa="sehat"
        )
        db.session.add(history)
        db.session.commit()
        new_history_id = history.id
        print("None of the names were found in the output.")
        return jsonify({"msg": "SUKSES", "id_hasil": new_history_id})
        return jsonify({"msg": "Gagal, Tidak Terdeteksi Wajah"})
    