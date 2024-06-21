# Deteksi-penyakit-mata-pada-anak-YOLOv8
Instal Tesseract OCR:
# Mengatasi TesseractNotFoundError pada Pytesseract

Error `TesseractNotFoundError` menunjukkan bahwa Tesseract OCR tidak ditemukan di sistem Anda atau tidak diatur dalam variabel PATH. Berikut adalah langkah-langkah untuk mengatasi masalah ini:

## 1. Instal Tesseract OCR

Unduh dan instal Tesseract OCR sesuai dengan sistem operasi Anda:

- [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki)
- [Linux (via package manager)](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- [MacOS (via Homebrew)](https://tesseract-ocr.github.io/tessdoc/Homebrew.html)

**Contoh untuk Windows**:

Unduh installer dari link di atas dan jalankan installer tersebut.

## 2. Tambahkan Tesseract ke PATH

Setelah menginstal Tesseract, tambahkan direktori instalasi Tesseract ke variabel PATH sistem Anda.

### Windows

1. Buka `Control Panel > System and Security > System > Advanced system settings`.
2. Klik tombol `Environment Variables`.
3. Di bawah `System variables`, temukan variabel `Path` dan klik `Edit`.
4. Tambahkan direktori tempat `tesseract.exe` diinstal. Misalnya, jika Anda menginstalnya di `C:\Program Files\Tesseract-OCR`, tambahkan path ini ke daftar.
5. Klik `OK` untuk menyimpan perubahan.

### Linux

Biasanya, menginstal Tesseract melalui package manager akan menambahkannya ke PATH secara otomatis.

Anda bisa mengecek dengan perintah `which tesseract` di terminal.

### MacOS

Setelah menginstal via Homebrew, path seharusnya sudah otomatis terkonfigurasi. Jika tidak, Anda bisa menambahkannya secara manual.

Cek dengan `which tesseract` di terminal.

## 3. Cek Instalasi

Buka terminal atau command prompt dan jalankan perintah berikut untuk memastikan bahwa Tesseract dapat diakses dan berfungsi dengan benar:

```sh
tesseract --version

