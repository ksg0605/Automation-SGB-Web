from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from werkzeug.utils import secure_filename
import os
from time import sleep
from spreadsheet import Spreadsheet
from gpt_client import GPTClient
from report_generator import ReportGenerator

UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

# 진행 상태를 저장할 변수
progress = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    global progress
    progress = {}  # 새 업로드에 대해 progress 초기화

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

        def generate_reports():
            global progress
            try:
                spreadsheet = Spreadsheet(file_path=file_path, sheet_name=sheet_name)
                gpt_client = GPTClient(api_key=api_key, model=gpt_version)
                report_generator = ReportGenerator(spreadsheet=spreadsheet, gpt_client=gpt_client, max_col=12, answers=answers, system_input=system_input)
                
                report_name = f"report_{filename}"
                report_path = os.path.join(app.config['REPORTS_FOLDER'], report_name)

                max_row = report_generator.spreadsheet.get_max_row()
                completed_rows = 0

                for row in range(2, max_row + 1):
                    report_generator.process_row(row)
                    completed_rows += 1
                    progress['status'] = f"{completed_rows} / {max_row-1} 완료 ({(completed_rows / (max_row-1)) * 100:.2f}%)"
                    sleep(1)  # 시뮬레이션을 위해 sleep 추가

                report_generator.spreadsheet.save(report_path)
                progress['status'] = "완료되었습니다"
                progress['download_url'] = f"/download/{report_name}"

            except Exception as e:
                progress['status'] = f"에러 발생: {str(e)}"

        from threading import Thread
        thread = Thread(target=generate_reports)
        thread.start()

        return jsonify({"message": "생기부 생성 작업이 시작되었습니다."})
        
    else:
        return jsonify({"message": "허용된 파일 형식이 아닙니다."}), 400

@app.route('/progress', methods=['GET'])
def get_progress():
    global progress
    return jsonify(progress)

@app.route('/download/<filename>', methods=['GET'])
def download_report(filename):
    return send_from_directory(app.config['REPORTS_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)
    app.run(debug=True)