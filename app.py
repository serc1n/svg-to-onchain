from flask import Flask, render_template, request, send_file, jsonify, Response
from typing import Union
import os
import tempfile
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from svg_to_json import convert_svg_to_json

app: Flask = Flask(__name__)

# Use temp directory for Vercel
UPLOAD_FOLDER = tempfile.gettempdir()
OUTPUT_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert() -> Union[tuple[dict, int], dict]:
    print("Starting conversion request")  # Debug log
    response = jsonify({'error': 'Invalid request'})
    response.headers['Content-Type'] = 'application/json'
    
    if 'file' not in request.files:
        print("No file in request")  # Debug log
        response = jsonify({'error': 'No file part'})
        return response, 400
    
    file: FileStorage = request.files['file']
    name: str = request.form.get('name', 'Untitled')
    print(f"Processing file: {file.filename}, name: {name}")  # Debug log
    
    if file.filename == '':
        print("Empty filename")  # Debug log
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Convert SVG
        try:
            svg_content = file.read().decode('utf-8')
            print(f"SVG content length: {len(svg_content)}")  # Debug log
            
            result = convert_svg_to_json(svg_content, name)
            print("Conversion successful")  # Debug log
            
            response = jsonify({
                'success': True,
                'result': result,
                'filename': secure_filename(file.filename).rsplit('.', 1)[0] + '.txt'
            })
            # Add CORS headers
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            error_response = jsonify({'error': str(e)})
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response, 500
        
    print("Invalid file type")  # Debug log
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/convert', methods=['OPTIONS'])
def handle_options():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

@app.route('/download/<filename>')
def download(filename: str) -> Response:
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename),
                    as_attachment=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    # Add CSP headers
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

@app.errorhandler(500)
def handle_500(e):
    return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)
