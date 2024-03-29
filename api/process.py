from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import openai
import mimetypes
import PyPDF2
import docx

# Load the API key from the environment variable
openai.api_key = os.environ['OPENAI_API_KEY']\


# Function to handle GPT-3 and GPT-4 model requests
def handle_gpt_request(model, prompt):
    if model == "GPT-3.5 Turbo":  # Example for GPT-3.5 Turbo
        model_id = "gpt-3.5-turbo"
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    elif model == "GPT-4":  # Example for GPT-4
        model_id = "gpt-4"  # Replace with the correct identifier for GPT-4 if different
        response = openai.Completion.create(
            model=model_id, prompt=prompt, max_tokens=150
        )
        return response.choices[0].text
    # ... Add other models as needed


# Function to extract text from PDF using PdfReader
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        return str(e)

# Function to extract text from a Word document
def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return str(e)

# Function to generate images using DALL-E or another image generation model (placeholder)
def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        # Assuming the response contains an image URL
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"Error generating image: {e}"

# Custom ChatGPT Model
def CustomChatGPT(user_input, model_choice, uploaded_file=None):
    # Handling file uploads and inputs
    if uploaded_file is not None:
        if isinstance(uploaded_file, list):
            file = uploaded_file[0]
        else:
            file = uploaded_file
        mime_type, _ = mimetypes.guess_type(file.name)
        
        if mime_type == 'application/pdf':
            file_text = extract_text_from_pdf(file)
        elif mime_type == 'application/msword' or mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_text = extract_text_from_docx(file)
        else:
            file_text = ""

        user_input += "\n\nFile Text:\n" + file_text

    # Determine which model to use
    if model_choice == "GPT-3.5 Turbo":
        model = "gpt-3.5-turbo-0613"  # Correct identifier for GPT-3.5 Turbo
    elif model_choice == "GPT-4":
        model = "davinci-002"  # Correct identifier for GPT-4
    elif model_choice == "DALL-E":
        image_url = generate_image(user_input)
        return image_url
    else:
        return "Invalid model selection."

    # Process the request with the chosen model
    return handle_gpt_request(model, user_input)

# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}

def handler(request):
    if request.method == 'POST':
        user_input = request.form.get('user_input', '')
        model_choice = request.form.get('model_choice', '')
        uploaded_file = request.files.get('file_attachment', None)

        file_text = ""
        if uploaded_file and allowed_file(uploaded_file.filename):
            if uploaded_file.filename.endswith('.pdf'):
                file_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.filename.endswith('.docx'):
                file_text = extract_text_from_docx(uploaded_file)
            
            combined_input = f"{user_input}\n\n[Extracted File Text]\n{file_text}" if file_text else user_input
        else:
            combined_input = user_input

        if model_choice == "DALL-E":
            response = generate_image(combined_input)
        else:
            response = handle_gpt_request(model_choice, combined_input)

        return jsonify({'response': response})

    else:
        return jsonify({'error': 'Method not allowed'}), 405