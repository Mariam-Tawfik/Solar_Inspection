from forms import RegistrationForm , LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from backend.yolo_processing import classify_thermal_PV
from backend.yolo_processing import segment_PV ,waypoints_planning
from io import BytesIO  # Import BytesIO

import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template ,url_for ,flash, redirect, request, send_file,jsonify
from reportlab.lib.colors import blue
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter  # Import letter module

from flask_restx import Resource, Api
import json
from flask_cors import CORS


app = Flask(__name__)
URL_Domain='https://0416-41-129-234-81.ngrok-free.app'


app.config['SECRET_KEY']='962d4d203bdebe514e6a4856b2fa1730279bb814a3cfc3e720277662f98aa9fb'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db' 

db=SQLAlchemy(app)


@app.route('/getJsonFile')
def get_json_file():
    # Load the JSON file
    with open('uploads/data.json', 'r') as file:
        json_data = json.load(file)
    
    # Return the JSON data
    return jsonify(json_data)

#@app.route("/")
@app.route("/home")
def home():
     return render_template('services.html')

@app.route("/about")
def about():
    return render_template('about.html',title="About")

@app.route('/card1')
def card1():
    return render_template('card1.html')


@app.route('/choosePath')
def choose_path():
    return render_template('choose_path.html')



@app.route('/handle_input', methods=['POST'])
def handle_input():
    # Get the uploaded files
    video_file = request.files.get('video')
    folder_files = request.files.getlist('folder')
    image_file = request.files.get('image')

    # Process the files using the appropriate function based on the type of input
    processed_data = {}

    if image_file:
        # Process individual image file (if provided)
        input_image_path = f"{image_file.filename}"
        image_file.save(input_image_path)
        output_image_path, total_time = classify_thermal_PV(input_image_path)
        os.remove(input_image_path)
        processed_data['image'] = {
            'total_time': f"{total_time:.2f} seconds",
            'image_path': output_image_path
        }

    elif folder_files:
        # Process images in the folder (if provided)
        processed_images = []
       
        for file in folder_files:
            if file.filename != '':
                filename = secure_filename(file.filename)
             
                # Save each image to a temporary location
                input_image_path = f"{filename}"
                file.save(input_image_path)
                output_image_path, total_time = classify_thermal_PV(input_image_path)
                os.remove(input_image_path)
                processed_images.append({
                    'filename': filename,
                    'total_time': f"{total_time:.2f} seconds",
                    'image_path': output_image_path
                })

        # Create a new folder to store processed images
        folder_path = os.path.dirname(file.filename)  # Extract folder name from file path
        folder_name = os.path.basename(folder_path)  # Get the folder name
        processed_folder_path = os.path.join('static', f"{folder_name}_processed")
        os.makedirs(processed_folder_path, exist_ok=True)

        # Move processed images to the new folder
        for processed_image in processed_images:
            old_path = processed_image['image_path']
            new_path = os.path.join(processed_folder_path, processed_image['filename'])
            
            # Check if the target file already exists
            if os.path.exists(new_path):
                # Generate a new filename if it already exists
                base, ext = os.path.splitext(processed_image['filename'])
                count = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(processed_folder_path, f"{base}_{count}{ext}")
                    count += 1
            
            os.rename(old_path, new_path)
            processed_image['image_path'] = new_path

        processed_data['folder'] = processed_images

    # Pass the processed data including image_path to the template
    return render_template('processed_data.html', data=processed_data)

    # Get the uploaded files
    video_file = request.files.get('video')
    folder_files = request.files.getlist('folder')
    image_file = request.files.get('image')

    # Process the files using the appropriate function based on the type of input
    processed_data = {}

    if image_file:
        # Process individual image file (if provided)
        input_image_path = f"{image_file.filename}"
        image_file.save(input_image_path)
        output_image_path, total_time = classify_thermal_PV(input_image_path)
        os.remove(input_image_path)
        processed_data['image'] = {
            'total_time': f"{total_time:.2f} seconds",
            'image_path': output_image_path
        }

    elif folder_files:
        # Process images in the folder (if provided)
        processed_images = []
       
        for file in folder_files:
            if file.filename != '':
                filename = secure_filename(file.filename)
             
                # Save each image to a temporary location
                input_image_path = f"{filename}"
                file.save(input_image_path)
                print(input_image_path)
                output_image_path, total_time = classify_thermal_PV(input_image_path)
                os.remove(input_image_path)
                processed_images.append({
                    'filename': filename,
                    'total_time': f"{total_time:.2f} seconds",
                    'image_path': output_image_path
                })

        # Create a new folder to store processed images
        folder_path = os.path.dirname(file.filename)  # Extract folder name from file path
        folder_name = os.path.basename(folder_path)  # Get the folder name
        processed_folder_path = os.path.join('static', f"{folder_name}_processed")
        os.makedirs(processed_folder_path, exist_ok=True)

        # Move processed images to the new folder
        for processed_image in processed_images:
            old_path = processed_image['image_path']
            new_path = os.path.join(processed_folder_path, processed_image['filename'])
            
            # Check if the target file already exists
            if os.path.exists(new_path):
                # Generate a new filename if it already exists
                base, ext = os.path.splitext(processed_image['filename'])
                count = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(processed_folder_path, f"{base}_{count}{ext}")
                    count += 1
            
            os.rename(old_path, new_path)
            processed_image['image_path'] = new_path

        processed_data['folder'] = processed_images
    print("data=processed_data",processed_data)

    return render_template('processed_data.html', data=processed_data)


@app.route("/service" )
def service():
    return render_template('services.html',title='Service')



@app.route('/handle_form_data', methods=['POST'])
def handle_form_data():
   filename= request.form.get('filename')
   layer_name= request.form.get('layer_name')
   ################################### 
   with open("static/data.json", 'r') as f:
        gpsfile = json.load(f)
   data={'filename':filename ,'layer_name':layer_name,'GPS_file': ,'Images'}

   url=URL_Domain+'/api/processCAD'

   response = requests.post(url,json=data) # Domain
   print("before",response)
   if response.status_code == 200:
    with open('static/data.json', 'w') as f:
        json.dump(response.json(), f, indent=4)
        print(response)

   return render_template('choose_dxf.html')


@app.route('/')
@app.route('/choose_dxf', methods=['GET'])
def choose_dxf():
    return render_template('choose_dxf.html')



@app.route('/getDataJson',methods=['GET'])
def getDataJson():
    with open("static/data.json", 'r') as f:
        data = json.load(f)
        return data
    

    

@app.route('/view')
def view():
    return render_template('view.html')


@app.route('/handle_dxf_files')
def handle_dxf_files():
    import requests

    # Make a GET request to Service B's API endpoint
    url=URL_Domain+'/getDxfFiles'
    response = requests.get(url)  

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
      
        return data
    else:
        # Handle error
        return "Failed to retrieve data from Service B"


@app.route('/uploadCAD', methods=['POST'])
def uploadCAD():
    dxf_file = request.files['file']

    data={'file':dxf_file }
    url=URL_Domain+'/api/processCAD'
    response = requests.post(url,json=data) # Domain
    with open(f'static/{dxf_file.filename}', 'w') as f:
        data = json.dump(response,f)
    return render_template('view.html')



@app.route('/handle_ser_input', methods=['POST'])
def handle_ser_input():
    if request.method == 'POST':
        # Check if the 'image' file and other form fields are present in the request
        if 'image' in request.files:
            # Get the uploaded file
            image = request.files['image']
            
            # Get other form data: upper left and lower right corner GPS coordinates
            upper_left_lat = float(request.form.get('upper_left_lat'))
            upper_left_lon = float(request.form.get('upper_left_lon'))
            lower_right_lat = float(request.form.get('lower_right_lat'))
            lower_right_lon = float(request.form.get('lower_right_lon'))
            
            # Process the uploaded image and other form data here
            # Example: Save the image to a directory
            image_path = os.path.join('uploads', image.filename)
            image.save(image_path)
            
            # Call the waypoints_planning function to process the image and generate GPS file
            output_gps_file = waypoints_planning(image_path, upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon)
            
            if output_gps_file:
                return f'Image uploaded successfully! GPS file generated: {output_gps_file}'
            else:
                return 'Error processing image and generating GPS file.'



@app.route("/register" ,methods=["GET","POST"])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created successfully for {form.username.data}",'success')
        return redirect(url_for('home'))
    return render_template('register.html',title='Rigister',form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        if form.email.data=='mariam.abouzaid@gmail.com' and form.password.data=='PASS!!word123':
            flash('You have been logged in', 'success')
            return redirect(url_for('home'))
        else:
             flash('Log in unsuccessful', 'danger')
    return render_template('login.html',title='Login',form=form)

@app.route('/')
def index():
    # Read GPS points from the text file
    gps_points = []
    with open('static/test_part_gps.txt', 'r') as file:
        for line in file:
            # Parse each line and remove parentheses
            line = line.strip().replace('(', '').replace(')', '')
            # Split the line into individual coordinates
            start_lat, start_lng, end_lat, end_lng = map(float, line.split(','))
            # Append the GPS points to the list
            gps_points.append({'start': {'lat': start_lat, 'lng': start_lng}, 'end': {'lat': end_lat, 'lng': end_lng}})
    
    # Pass GPS points to the template
    return render_template('map.html', gps_points=json.dumps(gps_points))


if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)
