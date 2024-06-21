import torch,datetime
from flask import jsonify,request,session
from . import app,db,History
import pytesseract
# Load the model
model_path = "best.pt"
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
names: ['strabismus (mata juling)','ptosis (kelopak mata turun)','mata merah','mata bengkak','mata bintitan']  # type: ignore # class names
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
        print(result.stdout)  # Tambahkan logging untuk output proses
        # Cari folder predict terbaru di dalam save_path
        subfolders = [f.path for f in os.scandir(save_path) if f.is_dir()]
        latest_folder = max(subfolders, key=os.path.getmtime)  # Folder terbaru berdasarkan waktu modifikasi
        # Mendapatkan direktori saat ini
        project_directory = os.path.abspath(os.path.dirname(__file__))
        # Mendapatkan direktori induk dari project_directory
        parent_directory = os.path.dirname(project_directory)
        detected_file_path = os.path.join(parent_directory,latest_folder, random_name)
        detected_text = pytesseract.image_to_string(Image.open(detected_file_path))
        if detected_text.strip():  # Validasi apakah ada teks yang terbaca
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Simpan hasil OCR ke database
            history = History(
                nama=session['username'],
                nama_anak="Anak",  # Ganti sesuai kebutuhan
                usia_anak=5,  # Ganti sesuai kebutuhan
                tanggal_konsultasi=current_time,  # Ganti sesuai kebutuhan
                hasil_diagnosa=detected_text
            )
            db.session.add(history)
            db.session.commit()
        else:
            return jsonify({"error": "No text detected in the image"}), 400
        return jsonify({"detected_file_path":detected_file_path}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr}), 500