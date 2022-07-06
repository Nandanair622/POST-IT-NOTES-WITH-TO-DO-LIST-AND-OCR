from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from fileinput import filename
import io
from flask import Flask, render_template, request, url_for, Response
import pytesseract
import cv2
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract as tess
from datetime import datetime
from werkzeug.utils import secure_filename
import os

views = Blueprint('views', __name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024*1024*1000
app.config['UPLOAD_EXTENSIONS'] = ['.jpg','.png','.gif']
app.config['UPLOAD_PATH'] = 'uploads'


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('takeimg.html')

@views.route('/take', methods=['GET', 'POST'])
def take():
    if request.method=="POST":
        try:
            tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
            print(request.files)
            imagefile  = request.files.get('file1', '') 
            img = Image.open(imagefile)
            
            text = pytesseract.image_to_string(img)
            f = open("sample.txt", "a")
            f.truncate(0)
            f.write(text)
            f.close()
            return render_template('showtext.html', var=text)
        except:
            return render_template('error.html')
       
@views.route("/gettext")
def gettext():
    with open("sample.txt") as fp:
        src = fp.read()
    return Response(
        src,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=sample.txt"})
