from flask import Flask, render_template, flash, redirect, request
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

#UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

application = Flask(__name__)
app=application
app.config["SECRET_KEY"] = "my secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"The operation is {operation} and the filename is {filename}.")
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), imgProcessed)
            return filename
        case "cwebp":
            newFileName = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFileName, img)
            return newFileName
        case "cjpg":
            newFileName = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFileName, img)
            return newFileName
        case "cpng":
            newFileName = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFileName, img)
            return newFileName
        
        case "cblur":
           imgProcessed = cv2.GaussianBlur(img, (15, 15), 0)
           cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), imgProcessed)
           return filename
       
        case "csharpen":
           kernel = np.array([[0, -1, 0],
                              [-1, 5, -1],
                              [0, -1, 0]])
           imgProcessed = cv2.filter2D(img, -1, kernel)
           cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filename), imgProcessed)
           return filename


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        operation = request.form.get('operation')
        if 'file' not in request.files:
            flash('No file part')
            return "Error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')   
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            flash(f"The image after preprocessing is stored <a href='/static/{filename}' target='_blank'>here</a>", "success")
            return render_template("index.html")
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False)
