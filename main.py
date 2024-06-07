from forms import RegistrationForm , LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from backend.yolo_processing import classify_thermal_PV
from backend.yolo_processing import segment_PV ,waypoints_planning
from backend.video_preprocessing import extraction
from backend.efficientNetV2_model_processing import load_model, classify_image
from io import BytesIO  # Import BytesIO
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template ,url_for ,flash, redirect, request, send_file,jsonify
from reportlab.lib.colors import blue
import requests
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter  # Import letter module
from flask_restx import Resource, Api
import json
from flask_cors import CORS

from generate_pdf import (
    generate_pdf_rgb_image,
    generate_pdf_rgb_folder,
    generate_pdf_thermal_image,
    generate_pdf_thermal_folder,
    generate_pdf_thermal_rgb_images,
)


app = Flask(__name__)
URL_Domain='https://8206-45-247-72-132.ngrok-free.app'


app.config['SECRET_KEY']='962d4d203bdebe514e6a4856b2fa1730279bb814a3cfc3e720277662f98aa9fb'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db' 

db=SQLAlchemy(app)

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(folder_path, '..')))


@app.route('/getJsonFile')
def get_json_file():
    # Load the JSON file
    with open('uploads/data.json', 'r') as file:
        json_data = json.load(file)
    
    # Return the JSON data
    return jsonify(json_data)

@app.route("/")
@app.route("/home")
def home():
     return render_template('home.html')


@app.route("/choose_analysis_method")
def choose_analysis_method():
     return render_template('choose_analysis_method.html')


@app.route("/about")
def about():
    return render_template('about.html',title="About")

@app.route("/upload_dxf")
def upload_dxf():
    return render_template('upload_dxf.html',title="upload_dxf")


@app.route('/card1')
def card1():
    return render_template('card1.html')


@app.route('/choosePath')
def choose_path():
    return render_template('choose_path.html')

@app.route('/uploadfield')
def uploadfield():
    return render_template('uploadfield.html')



@app.route('/handle_input', methods=['POST'])
def handle_input():
    # Get the uploaded files
    video_file = request.files.get('video')
    
     # Get the uploaded files
    # Option 1: Individual Files or Folders   
    rgb_image = request.files.get('rgb_image')
    thermal_image =  request.files.get('thermal_image')
    rgb_folder = request.files.getlist('rgb_folder')
    thermal_folder = request.files.getlist('thermal_folder')
    rgb_video = request.files.get('rgb_video')
    thermal_video = request.files.get('thermal_video')
    
    # Option 2: Combined Files or Folders
    combined_rgb_image = request.files.get('combined_rgb_image')
    combined_thermal_image =  request.files.get('combined_thermal_image')
    combined_rgb_folder = request.files.getlist('combined_rgb_folder')
    combined_thermal_folder = request.files.getlist('combined_thermal_folder')
    combined_rgb_video = request.files.get('combined_rgb_video')
    combined_thermal_video = request.files.get('combined_thermal_video')



    # Process the files based on the type of input
    processed_data = {}
    if video_file:
        # Define the path to save the video
        video_path = os.path.join('uploads', video_file.filename)
        print('video path',video_path)
        # Save the video file
        video_file.save(video_path)
               
        # Run the extraction function
        extraction(video_path, 'uploads/folder', 'uploads/output')
        print('after')
     
        return 'Video file processed and extraction function executed.'


    elif rgb_image:
        # Process individual image file (if provided)
        input_image_path = secure_filename(rgb_image.filename)
        rgb_image.save(input_image_path)  
        model= load_model()
        defect_label, formatted_prob = classify_image(input_image_path, model)
        
        processed_data = {
            'formatted_prob':formatted_prob,
            'defect_type': defect_label,
            'rgb_image_path': input_image_path
        }
        #print("Generated URL:", url_for('static', filename=processed_data['rgb_image_path']))

    elif thermal_image:

         # Process individual image file (if provided)
        input_image_path = f"temp_{thermal_image.filename}"
        thermal_image.save(input_image_path)
        output_image_path, formatted_prob = classify_thermal_PV(input_image_path)
        os.remove(input_image_path)
   
        processed_data = {
            'formatted_prob':formatted_prob,
            'thermal_image_path': output_image_path
        }
     #   print("Generated URL:", url_for('static', filename=processed_data['thermal_image_path']))

    elif thermal_folder and len(thermal_folder) > 1:
        # Process images in the folder (if provided)
        processed_images = []
       
        for file in thermal_folder:
            
            if file.filename != '':
                filename = secure_filename(file.filename)
             
                # Save each image to a temporary location
                input_image_path = f"{filename}"
                file.save(input_image_path)
                #print(input_image_path)      
                output_image_path, total_time = classify_thermal_PV(input_image_path)
                os.remove(input_image_path)
                processed_images.append({

                    'filename': filename,
                    'total_time': f"{total_time:.2f} seconds",
                    'thermal_image_path': output_image_path
                })

        # Create a new folder to store processed images
        folder_path = os.path.dirname(file.filename)  # Extract folder name from file path
        folder_name = os.path.basename(folder_path)  # Get the folder name
        processed_folder_path = os.path.join('static', f"{folder_name}_processed")
        os.makedirs(processed_folder_path, exist_ok=True)

        # Move processed images to the new folder
        for processed_image in processed_images:
            old_path = processed_image['thermal_image_path']
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
            processed_image['thermal_image_path'] = new_path

        processed_data['thermal_folder'] = processed_images
       # print("data=processed_data",processed_data)

    elif rgb_folder and len(rgb_folder) > 1:
         processed_data['rgb_folder'] = []

         # Ensure the target directory exists
         rgb_folder_path = 'static/rgb_folder'
         if not os.path.exists(rgb_folder_path):
            os.makedirs(rgb_folder_path)

         for rgb_image in rgb_folder:

            if rgb_image.filename != '':
                 # Process individual image file (if provided)
                input_image_filename = secure_filename(rgb_image.filename) 
                input_image_path = os.path.join('static/rgb_folder', input_image_filename)
                rgb_image.save(input_image_path)
                model= load_model()
                defect_label,formatted_prob = classify_image(input_image_path, model)
               # os.remove(input_image_path)

                 # Store processed data for current image in the list
                processed_data['rgb_folder'].append({
                    'formatted_prob':formatted_prob,
                    'defect_type': defect_label,
                    'rgb_image_path': input_image_path
                })
        # Zip the processed folder
            zip_filename = "rgb_folder_processed.zip"
            zip_filepath = os.path.join('static', zip_filename)
            zip_folder(rgb_folder_path, zip_filepath)

            # # Send the zip file to the external API
            url = URL_Domain + '/uploadRGB'
            with open(zip_filepath, 'rb') as zip_file:
                 files = {'file': (zip_filename, zip_file, 'application/zip')}
                 response = requests.post(url, files=files)

            # print(response)

         #print(processed_data)

    elif combined_rgb_image and combined_thermal_image:

        # RGB_image_processing
        rgb_image_path = secure_filename(combined_rgb_image.filename)
        combined_rgb_image.save(rgb_image_path)  
        model= load_model()
        defect_label, formatted_prob = classify_image(rgb_image_path, model)
        

        # thermal_image_processing
        thermal_image_path = f"temp_{combined_thermal_image.filename}"
        combined_thermal_image.save(thermal_image_path)
        output_image_path, total_time= classify_thermal_PV(thermal_image_path)
        os.remove(thermal_image_path)

        processed_data = {
            'formatted_prob':formatted_prob,
            'defect_type': defect_label,
            'combined_rgb_image_path': rgb_image_path,
            'total_time': f"{total_time:.2f} seconds",
            'combined_thermal_image_path': output_image_path
        }
   
    elif combined_rgb_folder and len(combined_rgb_folder) > 1 and combined_thermal_folder and len(combined_thermal_folder) > 1 :
        processed_data['combined_rgb_thermal_folder'] = []

        # Iterating over RGB and thermal images simultaneously
        for rgb_image, thermal_image in zip(combined_rgb_folder, combined_thermal_folder):
            if rgb_image.filename != '' and thermal_image.filename != '':
                # Process RGB image
                rgb_input_image_filename = rgb_image.filename.replace('combined_rgb_folder/', '')  # Remove the prefix
                rgb_input_image_path = secure_filename(rgb_input_image_filename)
                rgb_image.save(rgb_input_image_path)
                model = load_model()
                rgb_defect_label, rgb_formatted_prob = classify_image(rgb_input_image_path, model)

                # Process thermal image
                thermal_input_image_filename = thermal_image.filename.replace('combined_thermal_folder/', '')  # Remove the prefix
                thermal_input_image_path = secure_filename(thermal_input_image_filename)
                thermal_image.save(thermal_input_image_path)
                thermal_output_image_path,total_time = classify_thermal_PV(thermal_input_image_path)
                os.remove(thermal_input_image_path)

                # Store processed data for the current images
                processed_data['combined_rgb_thermal_folder'].append({
                    'rgb_formatted_prob': rgb_formatted_prob,
                    'rgb_defect_type': rgb_defect_label,
                    'rgb_image_path': rgb_input_image_path,
                    'total_time': f"{total_time:.2f} seconds",
                    'thermal_image_path': thermal_output_image_path
                })

        # Print the combined data
        #print(processed_data['combined_rgb_thermal_folder'])   

    elif rgb_video or thermal_video or combined_rgb_video or combined_thermal_video:
         # Process video file (if provided)
        processed_data = "Video processing not supported yet"

    else:
        print("No input!")

    # Save processed data to JSON file
    with open('processed_data.json', 'w') as json_file:
        json.dump(processed_data, json_file)
    
    return render_template('processed_data.html', data=processed_data )

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # Load processed data from JSON file
    with open('processed_data.json', 'r') as json_file:
        data = json.load(json_file)

    # Handling option 1
    if 'rgb_image_path' in data:
        pdf_buffer = generate_pdf_rgb_image(data)
    elif 'thermal_image_path' in data:
        pdf_buffer = generate_pdf_thermal_image(data['thermal_image_path'])
    elif 'rgb_folder' in data:
        pdf_buffer = generate_pdf_rgb_folder(data['rgb_folder'])
    elif 'thermal_folder' in data:
        pdf_buffer = generate_pdf_thermal_folder(data['thermal_folder'])

    # Handling option 2
    elif 'combined_rgb_image_path' in data and 'combined_thermal_image_path' in data:
        pdf_buffer = generate_pdf_thermal_rgb_images(data)
    
    # elif 'combined_rgb_thermal_folder' in data:
    #     pdf_buffer = generate_pdf_thermal_rgb_folders(data['combined_rgb_thermal_folder'])
  
    else:
        return "Error: Option is not supported", 400

    return send_file(pdf_buffer, as_attachment=True, mimetype='application/pdf', download_name='SolarInspect_Report.pdf')

@app.route("/service" )
def service():
    return render_template('services.html',title='Service')

@app.route('/handle_form_data', methods=['POST'])
def handle_form_data():
   filename= request.form.get('filename')
   layer_name= request.form.get('layer_name')
   ################################### 
   with open("satellite/complete_gps_file.json", 'r') as f:
        gpsfile = json.load(f)
    # data={'filename':filename ,'layer_name':layer_name,'GPS_file': ,'Images'}
   data={'filename':filename ,'layer_name':layer_name,'gps_coordinates':gpsfile}

   url=URL_Domain+'/api/processCAD'

   response = requests.post(url,json=data) # Domain
   print("before",response)
   if response.status_code == 200:
    with open('static/data.json', 'w') as f:
        json.dump(response.json(), f, indent=4)
        print(response)

   return render_template('choose_path.html')


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
        return "Failed to retrieve data"


@app.route('/uploadCAD', methods=['POST'])
def uploadCAD():
    dxf_file = request.files['file']

    data={'file':dxf_file }
    url=URL_Domain+'/api/processCAD'
    response = requests.post(url,json=data) # Domain
    with open(f'static/{dxf_file.filename}', 'w') as f:
        data = json.dump(response,f)
    return render_template('view.html')



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

@app.route('/handle_field_info', methods=['POST'])
def handle_field_info():
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
            
             # Process form data
            gps_points = process_form_data(image, upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon)
            return render_template('upload_dxf.html')

        

def process_form_data(image, upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon):
    # Process the uploaded image and other form data here
    image_path = os.path.join('uploads/', image.filename)
    print('image_path', image_path)
    image.save(image_path)
    
    # Call the waypoints_planning function to process the image and generate GPS file
    output_gps_file = waypoints_planning(image_path, upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon)
    output_gps_file = os.path.join('gps_output/', output_gps_file)
   

    print(output_gps_file)
    
    if output_gps_file:
        gps_points = []
        with open(output_gps_file, 'r') as file:
            for line in file:
                line = line.strip().replace('(', '').replace(')', '')
                start_lat, start_lng, end_lat, end_lng = map(float, line.split(','))
                gps_points.append({'start': {'lat': start_lat, 'lng': start_lng}, 'end': {'lat': end_lat, 'lng': end_lng}})
        return gps_points, output_gps_file
    else:
        return None, None



@app.route('/handle_ser_input', methods=['POST'])
def handle_ser_input():
    if request.method == 'POST':
        if 'image' in request.files:
            image = request.files['image']
            upper_left_lat = float(request.form.get('upper_left_lat'))
            upper_left_lon = float(request.form.get('upper_left_lon'))
            lower_right_lat = float(request.form.get('lower_right_lat'))
            lower_right_lon = float(request.form.get('lower_right_lon'))

            gps_points, gps_file_path = process_form_data(image, upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon)
            
            if gps_points:
                return render_template('map.html', gps_points=json.dumps(gps_points), gps_file_path=gps_file_path)
            else:
                return render_template('services.html')

@app.route('/download_gps_file', methods=['GET'])
def download_gps_file():
    gps_file_path = request.args.get('file_path')
    if gps_file_path and os.path.exists(gps_file_path):
        return send_file(gps_file_path, as_attachment=True, download_name=os.path.basename(gps_file_path), mimetype='text/plain')
    return "File not found", 404




if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)
