"""
PDF Tools — Flask backend
"""

from flask import Flask, request, jsonify, send_file, render_template
from io import BytesIO
from tools import TOOLS, TOOLS_BY_ID

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB max upload


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/tools")
def list_tools():
    """Return metadata for all registered tools."""
    return jsonify([t.to_dict() for t in TOOLS])


@app.route("/api/process/<tool_id>", methods=["POST"])
def process(tool_id: str):
    """
    Process files with the given tool.

    Expected multipart/form-data:
      - files[]: one or more PDF files
      - any extra options as form fields (e.g. degrees=90)
    """
    tool = TOOLS_BY_ID.get(tool_id)
    if not tool:
        return jsonify({"error": f"Ferramenta '{tool_id}' não encontrada."}), 404

    uploaded = request.files.getlist("files[]")
    if not uploaded or all(f.filename == "" for f in uploaded):
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    options = {k: v for k, v in request.form.items()}

    result = tool.process(uploaded, options)

    if "error" in result:
        return jsonify(result), 400

    return send_file(
        BytesIO(result["file"]),
        mimetype=result["mimetype"],
        as_attachment=True,
        download_name=result["filename"],
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
