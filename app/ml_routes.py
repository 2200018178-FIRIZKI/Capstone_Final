# app/ml_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required,
)  # Sesuaikan jika endpoint ini tidak perlu login
from app.ml_services import classify_data  # Impor fungsi utama dari ml_services

ml_bp = Blueprint("ml_bp", __name__, url_prefix="/ml")


@ml_bp.route("/predict", methods=["POST"])
# @jwt_required() # Aktifkan jika endpoint ini memerlukan pengguna untuk login
def handle_prediction_request_route():
    """
    Endpoint untuk menerima data dan mengembalikan prediksi dari model ML.
    Struktur input JSON harus disesuaikan dengan apa yang diharapkan oleh
    fungsi preprocess_input_for_model di ml_services.py.
    """
    if not request.is_json:
        return (
            jsonify({"error": "Request body harus berupa JSON"}),
            415,
        )  # Unsupported Media Type

    data = request.get_json()
    current_app.logger.info(f"Menerima request prediksi ke /ml/predict: {data}")

    # --- TENTUKAN INPUT UNTUK MODEL DARI DATA JSON ---
    # Ini adalah contoh. Anda HARUS menyesuaikannya.
    # Misalnya, jika Anda mengharapkan field "text" untuk klasifikasi teks:
    if "text_input" in data:
        input_for_model = data["text_input"]
    # Atau jika Anda mengharapkan field "features" berisi list angka:
    # elif 'features' in data:
    #     input_for_model = data['features']
    else:
        # Sesuaikan pesan error ini dengan field yang sebenarnya Anda harapkan
        return (
            jsonify(
                {
                    "error": "Input JSON tidak valid. Harap sertakan field yang benar (misalnya 'text_input' atau 'features')."
                }
            ),
            400,
        )

    if input_for_model is None or (
        isinstance(input_for_model, str) and not input_for_model.strip()
    ):
        return jsonify({"error": "Input untuk model tidak boleh kosong."}), 400
    # --- AKHIR PENENTUAN INPUT ---

    # Panggil fungsi klasifikasi/prediksi dari ml_services
    prediction_result = classify_data(input_for_model)

    # Periksa apakah ada 'error' dalam hasil prediksi dari service
    if isinstance(prediction_result, dict) and "error" in prediction_result:
        # Jika error dari service, kembalikan dengan status 500 atau sesuai jenis error
        error_message = prediction_result.get(
            "error", "Terjadi kesalahan pada pemrosesan ML."
        )
        current_app.logger.error(
            f"Error dari ml_service.classify_data: {error_message}"
        )
        # Sertakan detail error mentah jika ada, untuk debugging
        if "raw_prediction_for_debug" in prediction_result:
            return (
                jsonify(
                    {
                        "error": error_message,
                        "raw_prediction_detail": prediction_result[
                            "raw_prediction_for_debug"
                        ],
                    }
                ),
                500,
            )
        return jsonify({"error": error_message}), 500

    current_app.logger.info(f"Mengirim hasil prediksi: {prediction_result}")
    return jsonify(prediction_result), 200
