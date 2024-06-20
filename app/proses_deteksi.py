import torch
from flask import jsonify,request
from . import app,db
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

        # Baca hasil prediksi dari file JSON yang dihasilkan
        json_path = os.path.join(save_path, 'results.json')
        with open(json_path, 'r') as f:
            predictions = json.load(f)
            print(predictions)
        return jsonify(predictions), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr}), 500