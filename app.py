from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static"

# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def main():

    if request.method == "POST":

        language = request.form["language"]
        file = request.files["file"]

        if file:

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Upload audio to Gemini
            uploaded_file = client.files.upload(file=filepath)

            # Ask Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    uploaded_file,
                    f"""
                    Transcribe this audio.
                    Then translate it into {language}.
                    """
                ]
            )

            return jsonify({
                "result": response.text
            })

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)