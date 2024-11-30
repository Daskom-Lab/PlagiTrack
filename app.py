from flask import Flask, render_template, request, flash, redirect, url_for
import os
import shutil
from glob import glob
from utils import allowed_file, UPLOAD_FOLDER, process_detection

app = Flask(__name__)
app.secret_key = 'whyareyoureadingthis'

@app.route("/")
@app.route("/login")
def index():
	return render_template("index.html")

@app.route("/dashboard")
def dashboard():
	os.makedirs(UPLOAD_FOLDER, exist_ok=True)
	files = [file.removeprefix(UPLOAD_FOLDER+'/') for file in glob(UPLOAD_FOLDER+'/*.c')]
	return render_template("dashboard.html", files=files)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        flash('No file part in the request')
        return redirect(request.url)

    files = request.files.getlist('files')
    if not files:
        flash('No files selected')
        return redirect(request.url)

    for file in files:
        if file and allowed_file(file.filename):
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    flash('Files uploaded successfully.')
    return redirect(url_for('dashboard'))


@app.route('/delete', methods=['POST'])
def delete_files():
    shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)
    flash('All files deleted.')
    return redirect(url_for('dashboard'))


@app.route('/dashboard/result', methods=['POST', 'GET'])
def nue_detect():
    """Start scanning and detection."""	
    html_output = process_detection(glob(UPLOAD_FOLDER+'/*.c')[:8])
    return render_template('result.html', html_output=html_output)

if __name__ == '__main__':
	app.run(debug=True)