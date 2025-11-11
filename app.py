from flask import Flask, request, jsonify
import tempfile, os
from extractores import extractor_f  # importa tu único extractor

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ API de extracción activa (versión F)"

@app.route("/procesar", methods=["POST"])
def procesar():
    try:
        # Validar que haya archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se envió ningún archivo .txt"}), 400

        file = request.files['file']

        # Guardar temporalmente el archivo recibido
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            file.save(tmp.name)
            ruta = tmp.name

        # Procesar con el extractor
        datos, error = extractor_f.procesar_archivo(ruta)

        # Eliminar archivo temporal
        os.remove(ruta)

        # Responder con los datos
        return jsonify({
            "resultado": datos,
            "error": error
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Render usa la variable PORT automáticamente
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))