from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret-key"  # needed for session

app.config["UPLOAD_FOLDER"] = "static"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    language = request.form["language"]
    file = request.files["file"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    uploaded_file = client.files.upload(file=filepath)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            uploaded_file,
            f"""
            First transcribe this audio.
            Then translate it into {language}.

            Format:
            Transcription:
            ...

            Translation:
            ...
            """
        ]
    )

    session["result"] = response.text

    return redirect(url_for("result"))


@app.route("/result")
def result():
    result = session.get("result", None)
    return render_template("result.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)