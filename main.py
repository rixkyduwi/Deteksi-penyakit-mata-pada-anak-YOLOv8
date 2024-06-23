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
                "pengobatan": """tidak terdeteksi kejanggalan pada mata anak. tetap jaga kesehatan mata anak anda ...""",
                "link_gmaps": "tidak ada"
            },
            {
                "nama_penyakit": "strabismus (mata juling)",
                "pengobatan": """<ul>
        <li>Penggunaan kacamata khusus, untuk memperbaiki posisi bola mata bayi, agar kembali lurus.</li>
        <li>Penggunaan penutup mata (eye patch) selama beberapa jam per hari. Cara ini dapat melatih otot mata yang juling, sehingga kondisi juling dapat berkurang.</li>
        <li>Penggunaan obat tetes mata dengan kandungan atropin, yang diteteskan pada mata yang tidak juling agar pandangannya kabur, sehingga mata yang juling dilatih untuk melihat dengan fokus.</li>
        <li>segera periksakan dengan dokter apa bila mata tidak sembuh</li>
        </ul>""",
                "link_gmaps": "https://www.google.com/maps/search/klinik/"
            },
            {
                "nama_penyakit": 'ptosis (kelopak mata turun)',
                "pengobatan": """bawa ke rumah sakit terdekat segera""",
                "link_gmaps": "https://www.google.com/maps/search/rumah+sakit/"
            },
            {
                "nama_penyakit": 'mata merah',
                "pengobatan": """Mata merah atau konjungtivitis ...""",
                "link_gmaps": "https://www.google.com/maps/search/apotek/"
            },
            {
                "nama_penyakit": 'mata bengkak',
                "pengobatan": """bawa ke klinik segera""",
                "link_gmaps": "https://www.google.com/maps/search/klinik/"
            },
            {
                "nama_penyakit": 'mata bintitan',
                "pengobatan": """bawa ke klinik terdekat segera""",
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
