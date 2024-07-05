from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from spreadsheet import Spreadsheet
from gpt_client import GPTClient
from report_generator import ReportGenerator

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'file' not in request.files:
        return jsonify({"message": "파일을 업로드해주세요."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "파일 이름이 없습니다."}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        sheet_name = request.form['sheet_name']
        api_key = request.form['api_key']
        system_input = request.form['system_input']
        answers_str = request.form['answers']
        gpt_version = request.form['gpt_version']

        if not sheet_name or not api_key or not system_input or not answers_str:
            return jsonify({"message": "모든 필드를 채워주세요."}), 400

        answers = answers_str.split('\n')

        try:
            spreadsheet = Spreadsheet(file_path=file_path, sheet_name=sheet_name)
            gpt_client = GPTClient(api_key=api_key, model=gpt_version)
            report_generator = ReportGenerator(spreadsheet=spreadsheet, gpt_client=gpt_client, max_col=12, answers=answers, system_input=system_input)
            report_generator.generate_reports()
            return jsonify({"message": "생기부 생성 완료!"})
        
        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": "허용된 파일 형식이 아닙니다."}), 400

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)