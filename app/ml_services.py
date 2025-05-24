# app/ml_services.py
import os
from flask import current_app  # Untuk mengakses logger aplikasi

# Pilih salah satu cara impor Keras/TensorFlow berdasarkan instalasi Anda:
# Opsi 1: Jika menggunakan TensorFlow 2.x (umumnya ini)
from tensorflow import keras

# Opsi 2: Jika menggunakan Keras standalone versi lama (jarang sekarang)
# from keras.models import load_model

import numpy as np

# Impor library lain yang mungkin dibutuhkan untuk preprocessing, misalnya:
# import pickle # Jika ada tokenizer yang disimpan sebagai file .pickle
# from sklearn.preprocessing import StandardScaler # Contoh preprocessor
# from tensorflow.keras.preprocessing.sequence import pad_sequences # jika Keras tidak diimpor dari tensorflow.keras

# --- KONFIGURASI PATH MODEL ---
# Path ke direktori root proyek (tempat folder app/, ml_models/, dll. berada)
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)  # Naik satu level dari 'app'
MODEL_FILENAME = "model_ml.h5"  # Pastikan nama ini sesuai
MODEL_PATH = os.path.join(PROJECT_ROOT, "ml_models", MODEL_FILENAME)

# Jika ada file preprocessor lain yang perlu dimuat (misalnya tokenizer, scaler)
# Ganti dengan nama file preprocessor Anda dan pastikan ada di folder ml_models/
# TOKENIZER_FILENAME = 'tokenizer.pickle'
# TOKENIZER_PATH = os.path.join(PROJECT_ROOT, 'ml_models', TOKENIZER_FILENAME)
# SCALER_FILENAME = 'scaler.joblib'
# SCALER_PATH = os.path.join(PROJECT_ROOT, 'ml_models', SCALER_FILENAME)

# --- Variabel Global untuk Model dan Preprocessor ---
# Kita akan memuatnya sekali saja
ml_model = None
# tokenizer = None # Aktifkan jika Anda menggunakan tokenizer terpisah
# scaler = None    # Aktifkan jika Anda menggunakan scaler terpisah


def load_model_and_preprocessors():
    """
    Memuat model Keras/TensorFlow dari file .h5 dan preprocessor terkait (jika ada).
    Fungsi ini idealnya dipanggil sekali saat aplikasi Flask dimulai.
    """
    global ml_model  # , tokenizer, scaler # Aktifkan tokenizer, scaler jika digunakan

    if ml_model is None:  # Hanya muat jika belum dimuat
        if not os.path.exists(MODEL_PATH):
            current_app.logger.error(
                f"File model tidak ditemukan di path: {MODEL_PATH}"
            )
            raise FileNotFoundError(f"File model tidak ditemukan di path: {MODEL_PATH}")
        try:
            # Opsi 1 (TensorFlow 2.x):
            ml_model = keras.models.load_model(MODEL_PATH)
            # Opsi 2 (Keras standalone lama):
            # ml_model = load_model(MODEL_PATH)
            current_app.logger.info(
                f"Model ML '{MODEL_FILENAME}' berhasil dimuat dari: {MODEL_PATH}"
            )

            # --- CONTOH MEMUAT PREPROCESSOR (HARUS DISESUAIKAN!) ---
            # Jika Anda memiliki tokenizer yang disimpan:
            # if os.path.exists(TOKENIZER_PATH):
            #     with open(TOKENIZER_PATH, 'rb') as handle:
            #         tokenizer = pickle.load(handle)
            #     current_app.logger.info(f"Tokenizer '{TOKENIZER_FILENAME}' berhasil dimuat dari: {TOKENIZER_PATH}")
            # else:
            #     current_app.logger.warning(f"File tokenizer '{TOKENIZER_FILENAME}' tidak ditemukan di: {TOKENIZER_PATH}")

            # Jika Anda memiliki scaler yang disimpan:
            # if os.path.exists(SCALER_PATH):
            #     from joblib import load # Perlu install joblib: pip install joblib
            #     scaler = load(SCALER_PATH)
            #     current_app.logger.info(f"Scaler '{SCALER_FILENAME}' berhasil dimuat dari: {SCALER_PATH}")
            # else:
            #     current_app.logger.warning(f"File scaler '{SCALER_FILENAME}' tidak ditemukan di: {SCALER_PATH}")
            # --- AKHIR CONTOH MEMUAT PREPROCESSOR ---

        except Exception as e:
            current_app.logger.error(
                f"GAGAL memuat model ML ('{MODEL_FILENAME}') atau preprocessor: {e}"
            )
            ml_model = None  # Pastikan tetap None jika gagal
            raise e  # Re-raise exception agar bisa ditangkap saat startup jika perlu


def preprocess_input_for_model(input_data_raw):
    """
    Melakukan preprocessing pada input data mentah agar sesuai dengan format yang diharapkan model.
    >>> FUNGSI INI WAJIB ANDA ISI DENGAN LOGIKA PREPROCESSING DARI TEMAN ANDA <<<

    Ini adalah contoh placeholder. Anda HARUS menggantinya.
    Misalnya, jika model Anda menerima teks dan perlu tokenisasi & padding:
    """
    global tokenizer  # Jika Anda menggunakan tokenizer global
    current_app.logger.info(f"Preprocessing input mentah: {input_data_raw}")

    # ----- MULAI BAGIAN YANG PERLU DIGANTI SESUAI MODEL ANDA -----
    # Contoh jika model adalah klasifikasi teks dan Anda punya tokenizer:
    # if not tokenizer:
    #     raise ValueError("Tokenizer belum dimuat atau tidak ada.")
    # MAX_SEQUENCE_LENGTH = 200 # Ganti dengan maxlen yang benar untuk model Anda
    # if isinstance(input_data_raw, str):
    #     text_sequence = tokenizer.texts_to_sequences([input_data_raw])
    #     padded_sequence = keras.preprocessing.sequence.pad_sequences(text_sequence, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')
    #     current_app.logger.debug(f"Input diproses menjadi: {padded_sequence.shape}")
    #     return padded_sequence
    # else:
    #     raise TypeError("Input untuk model teks harus berupa string.")

    # Contoh jika model menerima array fitur numerik sederhana:
    # if isinstance(input_data_raw, list):
    #     input_array = np.array([input_data_raw]) # Pastikan shape-nya (1, num_features)
    #     # Jika ada scaler:
    #     # if not scaler:
    #     #     raise ValueError("Scaler belum dimuat atau tidak ada.")
    #     # input_array_scaled = scaler.transform(input_array)
    #     # return input_array_scaled
    #     return input_array # Jika tidak ada scaling
    # else:
    #     raise TypeError("Input untuk model numerik harus berupa list angka.")
    # ----- AKHIR BAGIAN YANG PERLU DIGANTI SESUAI MODEL ANDA -----

    current_app.logger.error(
        "KRUSIAL: Fungsi 'preprocess_input_for_model' belum diimplementasikan dengan benar!"
    )
    raise NotImplementedError(
        "Implementasikan fungsi preprocess_input_for_model sesuai kebutuhan model Anda."
    )


def postprocess_model_output(prediction_raw):
    """
    Mengubah output mentah dari model menjadi format yang lebih mudah dipahami/digunakan.
    >>> FUNGSI INI WAJIB ANDA ISI DENGAN LOGIKA POSTPROCESSING DARI TEMAN ANDA <<<

    Ini adalah contoh placeholder. Anda HARUS menggantinya.
    Misalnya, jika model Anda klasifikasi kategori:
    """
    current_app.logger.info(f"Postprocessing output mentah: {prediction_raw}")

    # ----- MULAI BAGIAN YANG PERLU DIGANTI SESUAI MODEL ANDA -----
    # Contoh jika output adalah probabilitas untuk beberapa kelas:
    # CLASS_LABELS = ['Berita', 'Olahraga', 'Teknologi', 'Hiburan'] # GANTI DENGAN LABEL KELAS ANDA
    # if isinstance(prediction_raw, np.ndarray) and prediction_raw.ndim > 1 and prediction_raw.shape[0] == 1:
    #     probabilities = prediction_raw[0]
    # elif isinstance(prediction_raw, np.ndarray) and prediction_raw.ndim == 1:
    #      probabilities = prediction_raw
    # else:
    #     current_app.logger.error(f"Format output model tidak dikenali: {type(prediction_raw)}, shape: {getattr(prediction_raw, 'shape', 'N/A')}")
    #     return {"error_postprocessing": "Format output model tidak dikenali", "raw_output": str(prediction_raw)}

    # try:
    #     predicted_class_index = np.argmax(probabilities)
    #     predicted_label = CLASS_LABELS[predicted_class_index]
    #     confidence_score = float(probabilities[predicted_class_index])

    #     all_scores = {label: float(prob) for label, prob in zip(CLASS_LABELS, probabilities) if len(CLASS_LABELS) == len(probabilities)}

    #     return {
    #         "predicted_category": predicted_label,
    #         "confidence": round(confidence_score, 4),
    #         "category_scores": all_scores
    #     }
    # except IndexError:
    #     current_app.logger.error(f"Index error saat postprocessing. Mungkin CLASS_LABELS tidak cocok dengan output model. Output: {probabilities}")
    #     return {"error_postprocessing": "Gagal memetakan prediksi ke label kelas.", "raw_output": probabilities.tolist()}
    # except Exception as e:
    #     current_app.logger.error(f"Error umum saat postprocessing: {e}")
    #     return {"error_postprocessing": str(e), "raw_output": probabilities.tolist() if 'probabilities' in locals() else str(prediction_raw)}
    # ----- AKHIR BAGIAN YANG PERLU DIGANTI SESUAI MODEL ANDA -----

    current_app.logger.error(
        "KRUSIAL: Fungsi 'postprocess_model_output' belum diimplementasikan dengan benar!"
    )
    # Kembalikan output mentah jika belum diimplementasikan
    if isinstance(prediction_raw, np.ndarray):
        return {"raw_prediction": prediction_raw.tolist()}
    return {"raw_prediction": str(prediction_raw)}  # Sebagai string jika bukan ndarray


def classify_data(input_data_raw):
    """
    Fungsi utama untuk melakukan klasifikasi/prediksi.
    """
    global ml_model
    if ml_model is None:
        current_app.logger.warning("Model ML belum dimuat. Mencoba memuat sekarang...")
        try:
            load_model_and_preprocessors()
            if ml_model is None:  # Jika masih None setelah mencoba muat
                current_app.logger.error("Model ML tidak dapat dimuat untuk prediksi.")
                return {"error": "Model machine learning tidak tersedia saat ini."}
        except Exception as e:
            current_app.logger.error(f"Gagal memuat model ML saat akan prediksi: {e}")
            return {"error": f"Gagal memuat model machine learning: {str(e)}"}

    try:
        processed_input = preprocess_input_for_model(input_data_raw)
    except NotImplementedError as e:
        return {"error": f"Preprocessing Error: {str(e)}"}
    except ValueError as e:
        return {"error": f"Input Error atau Preprocessing Error: {str(e)}"}
    except Exception as e:
        current_app.logger.error(
            f"Error tak terduga saat preprocessing input: {e}", exc_info=True
        )
        return {"error": "Terjadi kesalahan internal saat memproses input."}

    try:
        prediction_raw = ml_model.predict(processed_input)
    except Exception as e:
        current_app.logger.error(
            f"Error saat melakukan prediksi dengan model: {e}", exc_info=True
        )
        return {"error": "Terjadi kesalahan internal saat melakukan prediksi."}

    try:
        final_result = postprocess_model_output(prediction_raw)
    except NotImplementedError as e:
        return {
            "error": f"Postprocessing Error: {str(e)}",
            "raw_prediction_for_debug": (
                prediction_raw.tolist()
                if isinstance(prediction_raw, np.ndarray)
                else str(prediction_raw)
            ),
        }
    except Exception as e:
        current_app.logger.error(
            f"Error tak terduga saat postprocessing output: {e}", exc_info=True
        )
        return {
            "error": "Terjadi kesalahan internal saat memproses hasil prediksi.",
            "raw_prediction_for_debug": (
                prediction_raw.tolist()
                if isinstance(prediction_raw, np.ndarray)
                else str(prediction_raw)
            ),
        }

    return final_result
