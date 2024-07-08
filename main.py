from app import app, db, user_datastore, bcrypt,Rekomendasi,Profile
import flask_bcrypt

if __name__ == '__main__':
    # Tambahkan user dan admin awal
    with app.app_context():
        db.create_all()

        # Memastikan peran admin ada atau membuatnya jika tidak ada
        admin_role = user_datastore.find_role('admin')
        if not admin_role:
            admin_role = user_datastore.create_role(name='admin')
            db.session.commit()

        # Memastikan peran user ada atau membuatnya jika tidak ada
        user_role = user_datastore.find_role('user')
        if not user_role:
            user_role = user_datastore.create_role(name='user')
            db.session.commit()

        # Membuat admin user
        if not user_datastore.find_user(username='admin'):
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            admin = user_datastore.create_user(username="admin", password=hashed_password, active=True)
            user_datastore.add_role_to_user(admin, admin_role)
            db.session.commit()
        # Membuat regular user
        if not user_datastore.find_user(username='user'):
            hashed_password = bcrypt.generate_password_hash("user123").decode('utf-8')
            user = user_datastore.create_user(username="user", password=hashed_password, active=True)
            user_datastore.add_role_to_user(user, user_role)
            db.session.commit()
            profile = Profile(
                user_id = 2,
                full_name = "userr",
                email = "user@gmail.com",
                phone_number = "08-",
            )            
            db.session.add(profile)
            db.session.commit()

        # Membuat rekomendasi mata sehat
        rekomendasi_data = [
            {
                "nama_penyakit": "sehat",
                "pengobatan": """tidak terdeteksi kejanggalan pada mata anak. <br> tetap jaga kesehatan mata anak anda ...""",
                "link_gmaps": "/tips"
            },
            {
                "nama_penyakit": "strabismus (mata juling)",
                "pengobatan": """Terjadi karena tidak keseimbangan dan keharmonisan gerak otot otot bola mata (Ketika otot mata mengalami underaksi dan over aksi sehingga menyebabkan mata juling<br>
Bisa terjadi karena keturunan atau bawaan lahir, Masalah penglihatan pada satu mata, Jika salah satu mata memiliki masalah penglihatan yang signifikan, seperti rabun jauh atau rabun dekat yang tidak terkoreksi.<br>
<br>
Cara mengatasi :<br>
1.	Menggunakan Penutup mata (patching) tersedia di apotik : Metode ini melibatkan menutupi mata yang lebih kuat untuk mendorong mata yang lebih lemah bekerja lebih keras. Ini sering digunakan pada anak-anak untuk membantu memperkuat otot-otot mata yang lebih lemah.<br>
2.	Jika masalah terus berlanjut segera periksakan ke dokter,untuk mendapat penanganan lebih lanjut""",
                "link_gmaps": "https://www.google.com/maps/search/klinik/"
            },
            {
                "nama_penyakit": 'ptosis (kelopak mata turun)',
                "pengobatan": """Suatu keadaan dimana keadaan kelopak mata atas turun kebawah dari kedudukan mata normal,kedudukan normal itu ditepi kelopak mata kita 2 mm di dekat tepian mata atas,biasanya terjadi pada satu atau dua mata biasanya terjadi tanpa gejala.Akibatnya biasanya terkena gangguan lapang pandang,kesulitan melihat jauh atau dekat atau keadaan paling parah bisa terjadi mata malas pada anak<br>
Cara mengatasinya<br>
                1.	Penyebabnya biasanya terjadi bayi baru lahir atau bawaan terjadi karena otot otot untuk menikan kelopak mata sangat lemah<br>
2.	bisa juga terjadi karena adanya penyakit bawaan seperti tumor.<br>
Untuk ptosis sendiri memang tindakanya hanya oprasi saja,karena ditujukan untuk mengembalikan kelopak matanya seperti semula lagi,segera cari klinik mata terdekat untuk konsultasi dengan dokter
""",
                "link_gmaps": "https://www.google.com/maps/search/rumah+sakit/"
            },
            {
                "nama_penyakit": 'mata merah',
                "pengobatan": """Mata merah biasanya terjadi karena infeks iatau alergi Paparan asap, debu, angin, atau bahan kimia yang dapat menyebabkan mata merah<br>
Cara mengatasinya<br>
1.	Pastikan apakah mata yang terkena kemerahan hanya satu atau keduanya, karena jika hanya satu mata, kemungkinan besar terjadi infeksi.<br>
2.	Perhatikan apakah mata yang merah disertai dengan adanya belekan. Jika mata merah disertai belekan, dapat diteteskan antibiotik tetes mata yang tidak mengandung steroid, yang dapat dibeli di apotek terdekat. Jika kondisi ini berlanjut, segera kunjungi klinik terdekat dan konsultasikan dengan dokter.<br>
""",
                "link_gmaps": "https://www.google.com/maps/search/apotek/"
            },
            {
                "nama_penyakit": 'mata bengkak',
                "pengobatan": """Mata bengkak pada anak dapat disebabkan oleh berbagai factor seperti reaksi alergi terhadap debu, bulu hewan, atau bahan kimia dalam produk seperti sabun atau sampo dapat menyebabkan mata bengkak, gatal, dan berair,gigitan serangga atau saluran air mata tersumbat.<br>
Cara mengatasinya<br>
Kompres dingin:<br>
Gunakan kain bersih yang dibasahi dengan air dingin dan letakkan di atas mata yang bengkak selama beberapa menit. <br>
Hindari menyentuh atau menggosok mata:<br>
Ajari anak untuk tidak menggosok atau menyentuh matanya agar tidak memperburuk kondisi.<br>
Obat antihistamin:<br>
Jika pembengkakan disebabkan oleh alergi, obat antihistamin dapat membantu. Namun, pastikan untuk berkonsultasi dengan dokter sebelum memberikan obat ini kepada anak.<br>
Rekomendasi klinik terdekat""",
                "link_gmaps": "https://www.google.com/maps/search/klinik/"
            },
            {
                "nama_penyakit": 'mata bintitan',
                "pengobatan": """Mata bintitan (hordeolum) pada anak adalah kondisi di mana terjadi pembengkakan kecil, berwarna merah, dan terasa sakit di kelopak mata. Ini biasanya disebabkan oleh infeksi bakteri pada kelenjar minyak atau folikel bulu mata. <br>
Jangan mencoba memencet atau memecahkan bintitan, karena dapat memperburuk infeksi atau menyebarkannya ke area lain.<br>
<br>
Cara mengatasi :<br>
1.	Membeli salep atau tetes mata antibiotik di apotik untuk mengatasi infeksi.<br>
2.	Jika bintitan tidak sembuh dalam beberapa hari, terasa sangat sakit, atau disertai demam, segera bawa anak ke dokter untuk mendapatkan penanganan lebih lanjut.""",
                "link_gmaps": "https://www.google.com/maps/search/klinik/"
            }
        ]

        for rekomendasi in rekomendasi_data:
            if not Rekomendasi.query.filter_by(nama=rekomendasi['nama_penyakit']).first():
                new_rekomendasi = Rekomendasi(
                    nama=rekomendasi['nama_penyakit'],
                    pengobatan=rekomendasi['pengobatan'],
                    link_rekomendasi=rekomendasi['link_gmaps']
                )
                db.session.add(new_rekomendasi)
                db.session.commit()

    app.run(host="0.0.0.0", debug=True, port=4040)
