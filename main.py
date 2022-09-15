
from flask import Flask,flash, render_template,redirect,url_for, Response,request
import io
from werkzeug import secure_filename
import cv2
import os
import fonksiyonlar as fonk
from PIL import Image as im

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def kamera():
    
    license_cascade = cv2.CascadeClassifier('license_plate_cascade/cascade.xml') 
  
  
    # capture frames from a camera 
    cap = cv2.VideoCapture(0) 
  
    # loop runs if capturing has been initialized. 
    while True: 
  
        # reads frames from a camera 
        ret, img = cap.read() 
        

        # convert to gray scale of each frames 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        
        # Detects faces of different sizes in the input image 
        licenses = license_cascade.detectMultiScale(gray,5,20) 
        for (x,y,w,h) in licenses: 
        # To draw a rectangle in a face 
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2) 
            roi_gray = gray[y:y+h, x:x+w] 
            roi_color = img[y:y+h, x:x+w] 
  
  
        # Display an image in a window 
        encode_return_code, image_buffer = cv2.imencode('.jpg', img)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')
        # Wait for Esc key to stop 
        k = cv2.waitKey(30) & 0xff
        if k == 27: 
            break


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/kamera')
def video_feed():
    return Response(
        kamera(),
	mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/resim')
def home():
    return render_template('goruntu.html')

def goruntu(filename):
    img =fonk.resimAc(filename)
    img_gray=fonk.griyecevir(img)
    gurultuazalt=fonk.gurultuAzalt(img_gray)
    h_esitleme=fonk.histogramEsitleme(gurultuazalt)
    morfolojik_resim=fonk.morfolojikIslem(h_esitleme)
    goruntucikarma=fonk.goruntuCikarma(h_esitleme,morfolojik_resim)
    goruntuesikleme=fonk.goruntuEsikle(goruntucikarma)
    cannedge_goruntu=fonk.cannyEdge(goruntuesikleme)
    gen_goruntu=fonk.genisletmeIslemi(cannedge_goruntu)
    screenCnt=fonk.konturIslemi(img,gen_goruntu)
    yeni_goruntu=fonk.maskelemeIslemi(img_gray,img,screenCnt)
    son_goruntu = fonk.plakaIyilestir(yeni_goruntu)
    os.chdir('C:/Users/Lenovo/Desktop/elif_license_plate/static/saved')
    cv2.imwrite(filename,son_goruntu)

@app.route('/resim', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.chdir('C:/Users/Lenovo/Desktop/elif_license_plate/static/uploads')
        

        flash('Image successfully uploaded and displayed below')
        goruntu(filename)
        return render_template('goruntu.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


    
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='saved/' + filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
