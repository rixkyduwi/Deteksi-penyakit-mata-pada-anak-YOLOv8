import torch,datetime,re
from flask import jsonify,request,session
from . import app,db,History
import pytesseract
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
#model = ultralytics.YOLOv5Model(model='best.pt')
#results = model.detect(image_tensor)
#print(results)
import subprocess, json, os,uuid
from PIL import Image
from io import BytesIO
@app.route('/predict', methods=['POST'])
def predict():
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
    model_path = "./best.pt"
    save_path = "./app/static/detect"
    conf = 0.55
    print("loading..")
    # Perintah yang akan dijalankan
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
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout

        # Logging untuk output proses
        print(f"Command output: {output}")

        # Mengecek kemunculan setiap nama dalam output
        names= ['strabismus (mata juling)','ptosis (kelopak mata turun)','mata merah','mata bengkak','mata bintitan']  # class names
        found_names = ""
        for name in names:
            if name in output:
                found_names += name+","
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Cari folder predict terbaru di dalam save_path
        subfolders = [f.path for f in os.scandir(save_path) if f.is_dir()]
        latest_folder = max(subfolders, key=os.path.getmtime)  # Folder terbaru berdasarkan waktu modifikasi
        latest_folder = latest_folder.replace("./app/static/detect\\", "")
        detected_file_path = latest_folder+"/"+random_name
        print(detected_file_path)
        # Menampilkan hasil
        if found_names !="":
            print("Found names and their counts in output:")
            print(found_names)
            history = History(
                nama_user=session['full_name'],
                nama_anak=session['nama_anak'],  # Ganti sesuai kebutuhan
                usia_anak=session['usia_anak'],  # Ganti sesuai kebutuhan
                tanggal_konsultasi=current_time,  # Ganti sesuai kebutuhan
                file_deteksi = detected_file_path,
                hasil_diagnosa= found_names
                )
            db.session.add(history)
            db.session.commit()

            
            new_history_id = history.id  # Access the ID of the newly added profile
            return jsonify({"msg":"SUKSES","id_hasil":new_history_id})
        else:
            history = History(
                nama_user=session['full_name'],
                nama_anak=session['nama_anak'],  # Ganti sesuai kebutuhan
                usia_anak=session['usia_anak'],  # Ganti sesuai kebutuhan
                tanggal_konsultasi=current_time,  # Ganti sesuai kebutuhan
                file_deteksi = detected_file_path,
                hasil_diagnosa="sehat"
            )
            db.session.add(history)
            db.session.commit()
            new_history_id = history.id  # Access the ID of the newly added profile
            print("None of the names were found in the output.")
            return jsonify({"msg":"SUKSES","id_hasil":new_history_id})
        
    except subprocess.CalledProcessError as e:
        return jsonify({'msg': e.stderr}), 500