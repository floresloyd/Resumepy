from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import firebase_admin
from firebase_admin import credentials, storage
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

# FIREBASE 
cred = credentials.Certificate("key.json")


# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred, {'storageBucket': 'resumepy-55bb1.appspot.com'})
db = firestore.client()
resumes_ref = db.collection('resumes')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['UPLOAD_FOLDER'] = 'static/resumes'

# SUBMIT TO FIREBASE 
@app.route('/add', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        id = request.json['id']
        resumes_ref.document(id).set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

# Input Field and Submit field
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

# LINKS 
@app.route('/', methods=['GET', "POST"])


# RETURNS HTML FILE FOR WEBPAGE 
@app.route('/home',  methods=['GET', "POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # Grabs Resume
        uploadResume(file) # Upload to firebase 
        # file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename))) # Save file to resumes folder locally 
        
        return redirect("/submitted")
    return render_template('index.html', form=form)

# UPLOAD FUNCTION TO FIREBASE 
def uploadResume(file):
    path = '/resumes/'+str(secure_filename(file.filename))
    if file: 
        try:
            bucket = storage.bucket()
            #file is just an object from request.files e.g. file = request.files['myFile']
            blob = bucket.blob(file.filename)
            blob.upload_from_file(file)
        except Exception as e:
            print('error uploading user photo: ' % e)
    

# SUBMITTED REDIRECT 
@app.route('/submitted',  methods=['GET', "POST"])
def submitted():
    return render_template('submitted.html')



@app.errorhandler(404)
def invalid_route(e):
    return "Invalid Route."

if __name__ == '__main__':
    app.run(debug=True)
