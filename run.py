# run.py
import os
from app import create_app  # Impor fungsi application factory

# Dapatkan nama konfigurasi dari environment variable FLASK_ENV
# Jika tidak ada, default ke 'development'
config_name = os.environ.get("FLASK_ENV") or "development"

# Buat instance aplikasi menggunakan application factory
# dengan nama konfigurasi yang telah ditentukan.
app = create_app(config_name)

if __name__ == "__main__":
    # Jalankan server development Flask
    # host='0.0.0.0' membuat server dapat diakses dari luar (misalnya, dari IP lain di jaringan lokal)
    # port=5000 adalah port default Flask
    # debug=True akan mengaktifkan mode debug Flask, yang berguna saat pengembangan
    # Mode debug biasanya sudah diatur oleh FLASK_ENV=development,
    # tapi bisa juga diatur secara eksplisit di sini jika diperlukan.
    # app.config['DEBUG'] akan mengambil nilai dari konfigurasi yang dimuat.
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
