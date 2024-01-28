from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import openai
import mimetypes
import PyPDF2
import docx
import sys

absolute_path = "/api/process.py"
sys.path.append(absolute_path)

import process

# Initialize Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        model_choice = request.form.get('model_choice')
        uploaded_file = request.files.get('file')

        if uploaded_file:
            mime_type = mimetypes.guess_type(uploaded_file.filename)[0]
            if mime_type == 'application/pdf':
                file_text = process.extract_text_from_pdf(uploaded_file)
            # ... [handling other file types]
            user_input += "\n\nFile Text:\n" + file_text

        if model_choice == "DALL-E":
            image_url = process.generate_image(user_input)
            return jsonify({'image_url': image_url})
        else:
            response_text = process.handle_gpt_request(model_choice, user_input)
            return jsonify({'response_text': response_text})
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
