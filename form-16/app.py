
from flask import Flask,render_template,request,redirect,flash, send_file
from werkzeug.utils import secure_filename
import os
from pdf2image import convert_from_path
import easyocr
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json
import io
import cv2


    
app = Flask(__name__)
app.secret_key = "super secret key"
UPLOAD_FOLDER = '/Users/shivraj/Downloads/payslip 3/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = '/Users/shivraj/Downloads/payslip 3/json'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
EXTENSIONS = {'pdf', 'png', 'jpg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected','error')
            return render_template('index.html')
        if not allowed_file(file.filename):
            flash('Please upload the file in image or pdf format','error')
            #print(1)
            #print(request.files['file'].filename)
            return render_template('index.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(1)
            reader = easyocr.Reader(['en']) 
            if(filename[-3:]=='PDF' or filename[-3:]=='pdf'):
                images = convert_from_path(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                path1=app.config['UPLOAD_FOLDER']+'/'+filename[:-3]+'jpg'
                #print(len(images))
                line=''
                for j in images:
                    j.save(app.config['UPLOAD_FOLDER']+'/'+str(fil1)+'.png')
                    image = cv2.imread(app.config['UPLOAD_FOLDER']+'/'+str(fil1)+'.png')
                    print(image.shape)
                    fil1+=1
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                
                    # Remove horizontal lines
                    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
                    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
                    cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                    for c in cnts:
                        cv2.drawContours(thresh, [c], -1, (0,0,0), 2)
                    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,10))
                    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
                    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                    for c in cnts:
                        cv2.drawContours(thresh, [c], -1, (0,0,0), 2)
                    #cv2_imshow(thresh)
                    # Dilate to connect text and remove dots
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,1))
                    dilate = cv2.dilate(thresh, kernel, iterations=2)
                    #cv2_imshow(dilate)
                    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                    for c in cnts:
                        area = cv2.contourArea(c)
                        if area < 200:
                            cv2.drawContours(dilate, [c], -1, (255,255,255), -1)

                    result = cv2.bitwise_and(image, image, mask=dilate)
                    result[dilate==0] = (255,255,255)
                    #cv2_imshow(result)
                    result1 = reader.readtext(result,detail=0,paragraph=True)
                    #print(result1)
                    for res in result1:
                        line=line+' '+res
                print()
                print(line)
                print()
            else:
                image = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

                # Remove horizontal lines
                horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
                detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
                cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                for c in cnts:
                    cv2.drawContours(thresh, [c], -1, (0,0,0), 2)
                #cv2_imshow(thresh)
                # Dilate to connect text and remove dots
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,1))
                dilate = cv2.dilate(thresh, kernel, iterations=1)
                #cv2_imshow(dilate)
                cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if len(cnts) == 2 else cnts[1]
                for c in cnts:
                    area = cv2.contourArea(c)
                    if area < 200:
                        cv2.drawContours(dilate, [c], -1, (255,255,255), -1)

                result = cv2.bitwise_and(image, image, mask=dilate)
                result[dilate==0] = (255,255,255)
                #cv2_imshow(result)
                result1 = reader.readtext(result,detail=0,paragraph=True)
                #print(result1)
                line=''
                for res in result1:
                    line=line+' '+res
                print(4)
            nlp_ner = spacy.load("/Users/shivraj/Downloads/payslip 3/model/model-best")
            doc = nlp_ner(line)
            dict={}
            for i in doc.ents:
                dict[i.label_]=i.text
            with open(os.path.join(app.config['DOWNLOAD_FOLDER'], filename.rsplit('.', 1)[0]+'.json'), "w") as outfile:
                json.dump(dict, outfile)
                FILENAME =  filename.rsplit('.', 1)[0]+'.json'
                app.config['FILENAME'] = FILENAME
            flash('You can download your json file now','download')
            return redirect('/')
    else:
        return render_template('index.html')

@app.route('/download',methods=['GET', 'POST'])
def download():
    return send_file(app.config['DOWNLOAD_FOLDER']+'/'+app.config['FILENAME'],as_attachment=True)
    
if __name__ == "__main__":
    app.debug = True
    app.run()

