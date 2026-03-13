"""
PDF Tools — Flask backend
"""

from flask import Flask, request, jsonify, send_file, render_template
from io import BytesIO
from tools import TOOLS, TOOLS_BY_ID

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB max upload


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/tools")
def list_tools():
    return jsonify([t.to_dict() for t in TOOLS])


@app.route("/api/process/<tool_id>", methods=["POST"])
def process(tool_id: str):
    tool = TOOLS_BY_ID.get(tool_id)
    if not tool:
        return jsonify({"error": f"Ferramenta '{tool_id}' não encontrada."}), 404

    uploaded = request.files.getlist("files[]")
    if not uploaded or all(f.filename == "" for f in uploaded):
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    options = {k: v for k, v in request.form.items()}

    try:
        result = tool.process(uploaded, options)
    except MemoryError:
        return jsonify({"error": "Arquivo muito grande para processar no servidor gratuito. Tente com um arquivo menor."}), 500
    except Exception as e:
        app.logger.error(f"Unhandled error in tool '{tool_id}': {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao processar o arquivo. Verifique se o PDF não está corrompido e tente novamente."}), 500

    if "error" in result:
        return jsonify(result), 400

    return send_file(
        BytesIO(result["file"]),
        mimetype=result["mimetype"],
        as_attachment=True,
        download_name=result["filename"],
    )


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Arquivo(s) muito grande(s). O total enviado ultrapassa o limite de 200 MB."}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada."}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erro interno no servidor. Tente novamente."}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)
