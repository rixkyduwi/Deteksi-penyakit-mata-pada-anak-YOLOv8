# Deteksi-penyakit-mata-pada-anak-YOLOv8
Instal Tesseract OCR:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mengatasi TesseractNotFoundError pada Pytesseract</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }
        h1, h2, h3 {
            color: #333;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border: 1px solid #ddd;
            overflow-x: auto;
        }
        a {
            color: #0066cc;
        }
        .steps {
            margin-left: 20px;
        }
    </style>
</head>
<body>
    <h1>Mengatasi <code>TesseractNotFoundError</code> pada Pytesseract</h1>
    <p>Error <code>TesseractNotFoundError</code> menunjukkan bahwa Tesseract OCR tidak ditemukan di sistem Anda atau tidak diatur dalam variabel PATH. Berikut adalah langkah-langkah untuk mengatasi masalah ini:</p>
    
    <h2>1. Instal Tesseract OCR</h2>
    <p>Unduh dan instal Tesseract OCR sesuai dengan sistem operasi Anda:</p>
    <ul>
        <li><a href="https://github.com/UB-Mannheim/tesseract/wiki" target="_blank">Windows installer</a></li>
        <li><a href="https://tesseract-ocr.github.io/tessdoc/Installation.html" target="_blank">Linux (via package manager)</a></li>
        <li><a href="https://tesseract-ocr.github.io/tessdoc/Homebrew.html" target="_blank">MacOS (via Homebrew)</a></li>
    </ul>
    <p><strong>Contoh untuk Windows</strong>:</p>
    <div class="steps">
        <p>Unduh installer dari link di atas dan jalankan installer tersebut.</p>
    </div>
    
    <h2>2. Tambahkan Tesseract ke PATH</h2>
    <p>Setelah menginstal Tesseract, tambahkan direktori instalasi Tesseract ke variabel PATH sistem Anda.</p>
    
    <h3>Windows</h3>
    <ol>
        <li>Buka <code>Control Panel > System and Security > System > Advanced system settings</code>.</li>
        <li>Klik tombol <code>Environment Variables</code>.</li>
        <li>Di bawah <code>System variables</code>, temukan variabel <code>Path</code> dan klik <code>Edit</code>.</li>
        <li>Tambahkan direktori tempat <code>tesseract.exe</code> diinstal. Misalnya, jika Anda menginstalnya di <code>C:\Program Files\Tesseract-OCR</code>, tambahkan path ini ke daftar.</li>
        <li>Klik <code>OK</code> untuk menyimpan perubahan.</li>
    </ol>
    
    <h3>Linux</h3>
    <p>Biasanya, menginstal Tesseract melalui package manager akan menambahkannya ke PATH secara otomatis.</p>
    <p>Anda bisa mengecek dengan perintah <code>which tesseract</code> di terminal.</p>
    
    <h3>MacOS</h3>
    <p>Setelah menginstal via Homebrew, path seharusnya sudah otomatis terkonfigurasi. Jika tidak, Anda bisa menambahkannya secara manual.</p>
    <p>Cek dengan <code>which tesseract</code> di terminal.</p>
    
    <h2>3. Cek Instalasi</h2>
    <p>Buka terminal atau command prompt dan jalankan perintah berikut untuk memastikan bahwa Tesseract dapat diakses dan berfungsi dengan benar:</p>
    <pre>
        tesseract --version
    </pre>
</body>
</html>
