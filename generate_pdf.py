import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import blue
from reportlab.pdfgen import canvas
from io import BytesIO
import json


def generate_pdf_rgb_image(data):

    processed_image_path = data['rgb_image_path']
    defect = data['defect_type']

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

     # Add the logo
    logo_path = "drone.png"
    p.drawImage(logo_path, x=505, y=710, width=70, height=80) 

    # Add the title for the report
    p.setFillColor(blue)
    title = "SolarInspect Report"
    title_width = p.stringWidth(title, "Helvetica-Bold", 16)
    page_width, page_height = letter
    title_x = (page_width - title_width) / 2  # Center the title horizontally
    title_y = page_height - 50 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x, page_height - 50, title)  # Center the title vertically

    # draw a line
    p.line(0, title_y - 22, page_width, title_y - 22)
    p.setFillColorRGB(0, 0, 0)

    # Add page number
    p.setFont("Helvetica", 12)  
    p.drawString(page_width - 60, 30, f"Page 0")

    # Add copy write
    p.setFont("Helvetica", 8)
    p.drawRightString(page_width-550, 30, "© SolarInspect") 
    
    source_path= ""
    rgb_image_path = os.path.join(source_path, processed_image_path)
    x_coordinate= title_x-20
    y_coordinate= 480
    severity = ""
    suggested_action = ""
    shown_defect = ""

    # Add the processed image to the PDF
    if processed_image_path:

        p.drawImage(rgb_image_path, x=x_coordinate, y=y_coordinate,width=200, height=200)
        p.setFont("Helvetica-Oblique", 12) 
        p.drawString(title_x+40, 460, "Input RGB image")
    
        # Rename defect type
    if defect == 'clean':
        shown_defect = "Clean (No defect)"
    
    if defect ==  'bird_drop':
        shown_defect = "Bird Drop"

    if defect ==  'physical_damage':
        shown_defect = "Physical Damage"
    
    if defect ==  'Electrical_damage':
        shown_defect = "Electrical Damage"
    
    if defect ==  'dirty':
        shown_defect = "Dirty"

    # Add RGB Defect Type
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(60, 410, "RGB Defect Type: ")  
    p.setFont("Helvetica", 12) 
    p.drawString(220, 410, shown_defect)  

    if defect == 'bird_drop' or defect == 'dirty':
        suggested_action = "Cleaning"
        severity ="Minor"

    elif defect == 'Electrical_damage' or defect == 'physical_damage':
        suggested_action = "Repairing/Replacing"
        severity ="Major"

    elif defect == 'clean':
        suggested_action = "No action needed"
        severity ="No severity"
        
    else:
        "Unknown defect type!"

    # Add the severity 
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(60, 390, "Severity:") 
    p.setFont("Helvetica", 12)  
    p.drawString(220, 390, severity)

    # Add the suggested action 
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(60, 370, "Suggested Action:") 
    p.setFont("Helvetica", 12) 
    p.drawString(220, 370, suggested_action) 
   
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

def generate_pdf_rgb_folder(folder):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add the title for the report
    p.setFillColor(blue)
    title = "SolarInspect Report"
    title_width = p.stringWidth(title, "Helvetica-Bold", 16)
    page_width, page_height = letter
    title_x = (page_width - title_width) / 2  # Center the title horizontally
    title_y = page_height - 50 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x, page_height - 50, title)  # Center the title vertically

    # Add the logo
    logo_path = "drone.png"
    p.drawImage(logo_path, x=505, y=710, width=70, height=80) 

    # draw a line
    p.line(0, title_y - 22, page_width, title_y - 22)
    p.setFillColorRGB(0, 0, 0)

    # Add page number
    p.setFont("Helvetica", 12)  
    p.drawString(page_width - 60, 30, f"Page 0")

    # Add copy write
    p.setFont("Helvetica", 8)
    p.drawRightString(page_width-550, 30, "© SolarInspect") 

   # adding coordinates 
    source_path= ""
    x_coordinate= title_x-20
    y_coordinate= 480
    x_width= 60
    y_width= 220
    x_height = 460
    y_width = 410

    # Adding general statistics
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x+15, page_height - 100, "Field Panorama") 

    # Add the flight time
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(x_width, y_width-5, "Flight Time: ")
    p.setFont("Helvetica", 12)  
    p.drawString(270, y_width-5,"20 minutes") 

    #  Add the total number of panels in the field
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(x_width, y_width-30, "Total number of panels in the field:")  
    p.setFont("Helvetica", 12)  
    p.drawString(270, y_width-30, str(50))  

    #  Add the total number of inspected panels
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(x_width, y_width-55, "Total number of inspected panels:")  
    p.setFont("Helvetica", 12)  
    p.drawString( 270, y_width-55,str(40))  

    #  Add the percentage of inspected panels
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(x_width, y_width-80, "Percentage of inspected panels:")  
    p.setFont("Helvetica", 12)  
    p.drawString(270, y_width-80,"80 %") 

    p.showPage()

    print("rgb folder",folder)
    image_count = 0  # Initialize the image count variable
    page_number = 1  # Initialize page number variable
    severity = ""
    suggested_action = ""
    shown_defect = ""


    for rgb_image in folder:
        rgb_image_path = os.path.join(source_path, rgb_image['rgb_image_path'])
        id, row,center_longitude, center_latitude =  get_panel_info(image_count) # get the info of the panel
 
        # Add the RGB image to the PDF
        if 'rgb_image_path' in rgb_image:
            p.drawImage(rgb_image_path, x=x_coordinate, y=y_coordinate,width=200, height=200)
        
        # Add the logo
        logo_path = "drone.png"
        p.drawImage(logo_path, x=505, y=710, width=70, height=80) 

        # Add the title for the report
        p.setFillColor(blue)
        title = "SolarInspect Report"
        title_width = p.stringWidth(title, "Helvetica-Bold", 16)
        page_width, page_height = letter
        title_x = (page_width - title_width) / 2  # Center the title horizontally
        title_y = page_height - 50  
        p.setFont("Helvetica-Bold", 16)
        p.drawString(title_x, page_height - 50, title)  # Center the title vertically

        # draw a line
        p.line(0, title_y - 22, page_width, title_y - 22)
        p.setFillColorRGB(0, 0, 0)
           
        # Add the image number
        p.setFont("Helvetica-Bold", 12) 
        p.drawString(title_x+35, x_height, f" RGB Image {image_count + 1}") # Label the image
       
       # Rename defect type
        if rgb_image['defect_type'] == 'clean':
            shown_defect = "Clean (No defect)"
        
        if rgb_image['defect_type'] == 'bird_drop':
            shown_defect = "Bird Drop"

        if rgb_image['defect_type'] == 'physical_damage':
           shown_defect = "Physical Damage"
        
        if rgb_image['defect_type'] == 'Electrical_damage':
            shown_defect = "Electrical Damage"
        
        if rgb_image['defect_type'] == 'dirty':
            shown_defect = "Dirty"

        # Add the id of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x_width, y_width, "Panel ID:") 
        p.setFont("Helvetica", 12)  
        p.drawString(220, y_width, str(id)) 

        # Add the row number of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x_width, y_width-20, "Row Number:") 
        p.setFont("Helvetica", 12)  
        p.drawString(220, y_width-20, str(row)) 

        # Add RGB Defect Type
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x_width, y_width-40, "RGB Defect Type: ") 
        p.setFont("Helvetica", 12)  
        p.drawString( 220, y_width-40, shown_defect)

        if rgb_image['defect_type'] == 'bird_drop' or rgb_image['defect_type'] == 'dirty':
           suggested_action = "Cleaning"
           severity ="Minor"
        
        elif rgb_image['defect_type'] == 'Electrical_damage' or rgb_image['defect_type'] == 'physical_damage':
           suggested_action = "Repairing/Replacing"
           severity ="Major"
        
        elif rgb_image['defect_type'] == 'clean':
           suggested_action = "No action needed"
           severity ="No severity"
          
        else:
            "Unknown defect type!"
        

        # Add the severity 
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x_width, y_width-60, "Severity:") 
        p.setFont("Helvetica", 12)  
        p.drawString( 220, y_width-60,severity) 

         # Add the suggested action 
        p.setFont("Helvetica-Bold", 12) 
        p.drawString(350, y_width, "Suggested Action:")  
        p.setFont("Helvetica", 12)  
        p.drawString(500, y_width, suggested_action) 
        
        # Add the center longitude of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(350, y_width-20, "Center Longitude:")  
        p.setFont("Helvetica", 12)  
        p.drawString(500, y_width-20, center_longitude)  

        # Add the center latitude of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(350, y_width-40, "Center Latitude:")  
        p.setFont("Helvetica", 12) 
        p.drawString(500, y_width-40, center_latitude) 

        # Add page number
        p.drawString(page_width - 60, 30, f"Page {page_number}")

        p.showPage()

        image_count += 1  # Increment the image count
        page_number += 1  # Increment the page number
        
    p.save()

    buffer.seek(0)
    return buffer

def generate_pdf_thermal_image(processed_image_path):

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add the logo
    logo_path = "drone.png"
    p.drawImage(logo_path, x=505, y=710, width=70, height=80) 

    # Add the title for the report
    p.setFillColor(blue)
    title = "SolarInspect Report"
    title_width = p.stringWidth(title, "Helvetica-Bold", 16)
    page_width, page_height = letter
    title_x = (page_width - title_width) / 2  # Center the title horizontally
    title_y = page_height - 50 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x, page_height - 50, title)  # Center the title vertically

    # draw a line
    p.line(0, title_y - 22, page_width, title_y - 22)
    p.setFillColorRGB(0, 0, 0)

    # Add page number
    p.setFont("Helvetica", 12)  
    p.drawString(page_width - 60, 30, f"Page 0")

    # Add copy write
    p.setFont("Helvetica", 8)
    p.drawRightString(page_width-550, 30, "© SolarInspect") 

    source_thermal_path= "E:\\FlaskApp\\"
    thermal_image_path = os.path.join(source_thermal_path, processed_image_path)
    x_coordinate= title_x-20
    y_coordinate= 480

    # Add the processed image to the PDF
    if processed_image_path:

        p.drawImage(thermal_image_path, x=x_coordinate, y=y_coordinate,width=200, height=200)
        p.setFont("Helvetica-Oblique", 12)  # Set font style to italic
        p.drawString(title_x, 460, "Processed thermal image")
   
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

def generate_pdf_thermal_folder(folder):

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add the title for the report
    p.setFillColor(blue)
    title = "SolarInspect Report"
    title_width = p.stringWidth(title, "Helvetica-Bold", 16)
    page_width, page_height = letter
    title_x = (page_width - title_width) / 2  # Center the title horizontally
    title_y = page_height - 50 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x, page_height - 50, title)  # Center the title vertically

    # draw a line
    p.line(0, title_y - 22, page_width, title_y - 22)
    p.setFillColorRGB(0, 0, 0)

    # Add page number
    p.setFont("Helvetica", 12)  # Set font back to regular
    p.drawString(page_width - 60, 30, f"Page 0")

    # Add copy write
    p.setFont("Helvetica", 8)
    p.drawRightString(page_width-550, 30, "© SolarInspect") 

   # Adding coordinates 
    source_path= ""
    x_coordinate= title_x-20
    y_coordinate= 480
    x_width= 60
    y_width= 220
    x_height = 460
    y_width = 410

    # Adding general statistics
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x+15, page_height - 100, "Field Panorama") 

    # Add the flight time
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(x_width, y_width-5, "Flight Time: ")
    p.setFont("Helvetica", 12)  
    p.drawString(270, y_width-5,"20 minutes") 

    #  Add the total number of panels in the field
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(x_width, y_width-30, "Total number of panels in the field:")  
    p.setFont("Helvetica", 12)  
    p.drawString(270, y_width-30, str(50))  

    #  Add the total number of inspected panels
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(x_width, y_width-55, "Total number of inspected panels:")  
    p.setFont("Helvetica", 12)  
    p.drawString( 270, y_width-55,str(40))  

    #  Add the percentage of inspected panels
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(x_width, y_width-80, "Percentage of inspected panels:")  
    p.setFont("Helvetica", 12)  
    p.drawString(270, y_width-80,"80 %") 

    p.showPage()

    image_count = 0  # Initialize the image count variable
    page_number = 1  # Initialize page number variable

    for thermal_image in folder:

        id, row,center_longitude, center_latitude =  get_panel_info(image_count) # get the info of the panel
        thermal_image_path = os.path.join(source_path, thermal_image['thermal_image_path'])

          # Add the processed image to the report
        if 'thermal_image_path' in thermal_image:

            p.drawImage(thermal_image_path, x=x_coordinate, y=y_coordinate,width=200, height=200)


        # Add the logo
        logo_path = "drone.png"
        p.drawImage(logo_path, x=505, y=710, width=70, height=80) 

        # Add the title for the report
        p.setFillColor(blue)
        title = "SolarInspect Report"
        title_width = p.stringWidth(title, "Helvetica-Bold", 16)
        page_width, page_height = letter
        title_x = (page_width - title_width) / 2  # Center the title horizontally
        title_y = page_height - 50  
        p.setFont("Helvetica-Bold", 16)
        p.drawString(title_x, page_height - 50, title)  # Center the title vertically

        # draw a line
        p.line(0, title_y - 22, page_width, title_y - 22)
        p.setFillColorRGB(0, 0, 0)
            
        # Label the image
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(title_x+22, x_height, f" Thermal Image {image_count + 1}")

        # Add the id of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x_width,y_width-20, "Panel ID:")  
        p.setFont("Helvetica", 12)  
        p.drawString( 220, y_width-20,str(id) ) 
    
        # Add the row number of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(x_width, y_width-40, "Row Number:")  
        p.setFont("Helvetica", 12)  
        p.drawString(220, y_width-40, str(row))      
       
        # Add the center longitude of the panel
        p.setFont("Helvetica-Bold", 12)  
        p.drawString(350, y_width-20, "Center Longitude:")  
        p.setFont("Helvetica", 12)  
        p.drawString(500, y_width-20, center_longitude)  

        # Add the center latitude of the panel
        p.setFont("Helvetica-Bold", 12) 
        p.drawString(350, y_width-40, "Center Latitude:")
        p.setFont("Helvetica", 12)  
        p.drawString(500, y_width-40, center_latitude)

        # Add page number
        p.drawString(page_width - 60, 30, f"Page {page_number}")

        # Add copy write
        p.setFont("Helvetica", 8)
        p.drawRightString(page_width-550, 30, "© SolarInspect") 

        p.showPage()

        image_count += 1  # Increment the image count
        page_number += 1  # Increment the page number
       
    p.save() # save the pdf

    buffer.seek(0)
    return buffer


def format_coordinates(coord):
    return "{:.6f}°".format(coord)


def get_panel_info(panel_number):

    # Load the JSON file
    with open('data.json', 'r') as file:
        data = json.load(file)

    for item in data:
      if item.get('id') == panel_number:
        id = item.get('id')
        row = item.get('group')
        gps = item.get('gps')

         # Extract gps coordinates from gps if available
        if gps:
                gps_coordinates = gps.get('gps_coordinates')
                if gps_coordinates:
                    top_left = gps_coordinates.get('top_left')
                    bottom_right = gps_coordinates.get('bottom_right')
                else:
                    top_left  = bottom_right = None
        else:
                 top_left = bottom_right = None
        
         # Calculate center coordinates
        center_longitude = (top_left['longitude'] + bottom_right['longitude']) / 2
        center_latitude = (top_left['latitude'] + bottom_right['latitude']) / 2
       
        return id, row, format_coordinates(center_longitude), format_coordinates(center_latitude)


def generate_pdf_thermal_rgb_images(data):
    image_path_1 = data['combined_rgb_image_path']
    defect = data['defect_type']
    image_path_2 = data['combined_thermal_image_path']

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

     # Add the logo
    logo_path = "drone.png"
    p.drawImage(logo_path, x=505, y=710, width=70, height=80) 

    # Add the title for the report
    p.setFillColor(blue)
    title = "SolarInspect Report"
    title_width = p.stringWidth(title, "Helvetica-Bold", 16)
    page_width, page_height = letter
    title_x = (page_width - title_width) / 2  # Center the title horizontally
    title_y = page_height - 50 
    p.setFont("Helvetica-Bold", 16)
    p.drawString(title_x, page_height - 50, title)  # Center the title vertically

    # draw a line
    p.line(0, title_y - 22, page_width, title_y - 22)
    p.setFillColorRGB(0, 0, 0)

    # Add page number
    p.setFont("Helvetica", 12)  # Set font back to regular
    p.drawString(page_width - 60, 30, f"Page 0")

    # Add copy write
    p.setFont("Helvetica", 8)
    p.drawRightString(page_width-550, 30, "© SolarInspect") 
    
    source_path= ""
    rgb_image_path = os.path.join(source_path, image_path_1)
    thermal_image_path = os.path.join(source_path, image_path_2)
    x_coordinate= title_x-20
    y_coordinate= 480
    severity = ""
    suggested_action = ""
    shown_defect = ""

    # Add the processed image to the PDF
    if image_path_1:

        p.drawImage(rgb_image_path, x=x_coordinate-140, y=y_coordinate,width=200, height=200)
        p.setFont("Helvetica-Oblique", 12)  
        p.drawString(title_x-120, 460, "Processed RGB image")

    if image_path_2:
        p.drawImage(thermal_image_path, x=x_coordinate+140, y=y_coordinate,width=200, height=200)
        p.setFont("Helvetica-Oblique", 12)  
        p.drawString(title_x+150, 460, "Processed thermal image")

    
        # Rename defect type
    if defect == 'clean':
        shown_defect = "Clean (No defect)"
    
    if defect ==  'bird_drop':
        shown_defect = "Bird Drop"

    if defect ==  'physical_damage':
        shown_defect = "Physical Damage"
    
    if defect ==  'Electrical_damage':
        shown_defect = "Electrical Damage"
    
    if defect ==  'dirty':
        shown_defect = "Dirty"

    # Add RGB Defect Type
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(60, 410, "RGB Defect Type: ")  
    p.setFont("Helvetica", 12)  
    p.drawString(220, 410, shown_defect)  

    if defect == 'bird_drop' or defect == 'dirty':
        suggested_action = "Cleaning"
        severity ="Minor"

    elif defect == 'Electrical_damage' or defect == 'physical_damage':
        suggested_action = "Repairing/Replacing"
        severity ="Major"

    elif defect == 'clean':
        suggested_action = "No action needed"
        severity ="No severity"
        
    else:
        "Unknown defect type!"

    # Add the severity 
    p.setFont("Helvetica-Bold", 12)  
    p.drawString(60, 390, "Severity:")  
    p.setFont("Helvetica", 12)  
    p.drawString(220, 390, severity)

    # Add the suggested action 
    p.setFont("Helvetica-Bold", 12) 
    p.drawString(60, 370, "Suggested Action:") 
    p.setFont("Helvetica", 12) 
    p.drawString(220, 370, suggested_action)  
   
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
