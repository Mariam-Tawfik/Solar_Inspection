
import cv2
import numpy as np
from scipy.signal import find_peaks
from PIL import Image
from scipy import ndimage
import json
import os
from ultralytics import YOLO
import time
from PIL import Image


def classify_thermal_PV(input_image_path):
    # Load the trained YOLOv8 model
    start_time = time.time()
    model = YOLO('best.pt')

    # Load the input image
    input_image = Image.open(input_image_path)
    
        # Run inference
    results = model(input_image)
    total_time = time.time() - start_time

    # Handle the results
    output_images = []
    for i, result in enumerate(results):
        # Save output image in static folder
        output_directory = os.path.join('static')
        os.makedirs(output_directory, exist_ok=True)
        output_image_path = os.path.join(output_directory, f"{os.path.basename(input_image_path)}")
        result.save(output_image_path)
        output_images.append(output_image_path)
    
    # Check if there is something detected in the image
    return output_image_path, total_time


# input_image_path='uploads/image_367.png'

# output_image_path,total_time =classify_thermal_PV(input_image_path)
# print(output_image_path)

# def segment_PV(input_image_path):
#     import os
#     from ultralytics import YOLO
#     import time
#     from PIL import Image

#     # Load the trained YOLOv8 model
#     start_time = time.time()
#     model = YOLO('segment_weights.pt')
#         # Load the input image
#     input_image = Image.open(input_image_path)
    
#         # Run inference
#     #results = model(input_image)
#     results=model.predict(source=input_image,save = True, save_txt = True, show_labels = False, boxes = False)
#     total_time = time.time() - start_time
#     print(results)

#     # Handle the results
#     output_images = []
#     for i, result in enumerate(results):
#         # Save output image in static folder
#         output_directory = os.path.join('static')
#         os.makedirs(output_directory, exist_ok=True)
#         output_image_path = os.path.join(output_directory, f"{os.path.basename(input_image_path)}")
#         result.save(output_image_path)
#         output_images.append(output_image_path)
    
#     # Check if there is something detected in the image
#     return output_image_path, total_time
# #output_image_path, total_time=segment_PV('uploads/part.jpg')

def segment_PV(input_image_path):


    model = YOLO('segment_weights.pt')

    # Load the input image
    input_image = Image.open(input_image_path)

    # Run inference and save results
    results = model.predict(source=input_image, save=True, save_txt=True, project="satellite", name="labels")
    results_obj = results[0]
    input_filename = os.path.splitext(os.path.basename(input_image_path))[0]

    # Get the path to the saved labels file
    labels_file_path = os.path.join(results_obj.save_dir, "labels", input_filename + ".txt")

    return labels_file_path
def calculate_distance(point1, point2):
    # Calculate Euclidean distance between two points
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def nearest_neighbor(gps_points, start_point):
    ordered_points = []
    remaining_points = gps_points.copy()

    # Start from the specified start point


    current_point = start_point

    ordered_points.append(current_point)
    remaining_points.remove(current_point)

    # Find nearest neighbor until all points are covered
    while remaining_points:
        nearest_point = min(remaining_points, key=lambda x: calculate_distance(current_point[1], x[0]))
        ordered_points.append(nearest_point)
        current_point = nearest_point
        remaining_points.remove(nearest_point)

    return ordered_points

def pixel_to_gps(x, y):
    lon = lon1 + x * lon_per_pixel
    lat = lat1 - y * lat_per_pixel
    return lat, lon  # Note the order: latitude first, then longitude
def process_image(image_file_path,label_file_path,lat1,lon1,lat2,lon2):

    # Read the image
    image = cv2.imread(image_file_path)
    # Prepare the mask
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    # Read the segmented labels file and extract coordinates for each polygon
    if os.path.exists(label_file_path):
        with open(label_file_path, 'r') as file:
            for line in file:
                data = line.strip().split()[1:]  # Skip the first number (class object)
                coordinates = np.array(data, dtype=float).reshape(-1, 2)
                # Adjust coordinates for image dimensions (assuming they are normalized)
                coordinates *= np.array(image.shape[1::-1])  # width (x) and height (y)
                # Draw each polygon on the mask
                cv2.fillPoly(mask, [coordinates.astype(int)], color=255)

        # Apply the mask to the original image to get the segmented part
        segmented_part = cv2.bitwise_and(image, image, mask=mask)
        # Create a gray image
        gray_image = np.full_like(image, 0, dtype=np.uint8)  # You can adjust the gray level here

        # Invert the mask
        inverted_mask = cv2.bitwise_not(mask)

        # Apply the inverted mask to the gray image
        background = cv2.bitwise_and(gray_image, gray_image, mask=inverted_mask)

        # Merge the segmented part with the gray image
        result = cv2.add(segmented_part, background)
        cv2.imwrite('reult.jpg', result)
    else:
        result=image


    hist = cv2.calcHist([result], [0], None, [256], [0, 256]).flatten()
    hist = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)  # Normalize for better visibility

    # Smooth the histogram using a windowed filter
    window_size = 5
    smoothed_hist = np.convolve(hist, np.ones(window_size)/window_size, mode='same')

    # Detect peaks with a minimum distance between them to ensure they are far apart
    peaks, _ = find_peaks(smoothed_hist, distance=5)  # distance can be adjusted based on image characteristics

    # Define thresholds for ignoring peaks near the boundaries
    lower_bound = 3
    upper_bound = 250

    # Filter out peaks too close to 0 or 255
    filtered_peaks = [peak for peak in peaks if lower_bound < peak < upper_bound]

    if len(filtered_peaks) > 1:
        sorted_peaks = sorted(filtered_peaks, key=lambda x: smoothed_hist[x], reverse=True)
        major_peaks = sorted_peaks[:2]
        major_peaks.sort()

        # Find the valley between these two peaks as the minimum point
        valley_index = np.argmin(smoothed_hist[major_peaks[0]:major_peaks[1]]) + major_peaks[0]
    else:
        valley_index = np.median(filtered_peaks)  # Fallback if not enough peaks are found

    # Custom binary transformation
    # Custom binary transformation
    if valley_index < 100:
        _, thresholded_image = cv2.threshold(result, valley_index, 255, cv2.THRESH_BINARY)
    else:
        # Reverse transformation with exception for value 0
        thresholded_image = np.where((result > valley_index) | (result == 0), 0, 255).astype(np.uint8)  # Ensure uint8 type here

    # iterations of dilation and erosion
    # Dilate the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Adjust kernel size as needed
    eroded_image = cv2.erode(thresholded_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)) # Adjust kernel size as needed
    dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # Adjust kernel size as needed
    eroded_image = cv2.erode(dilated_image, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # Adjust kernel size as needed
    dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)


    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # Adjust kernel size as needed
    eroded_image = cv2.erode(dilated_image, kernel, iterations=1)
    cv2.imwrite('final_image.jpg', eroded_image)


    blur_radius = 1.0
    threshold = 50
    
    img = Image.open('final_image.jpg').convert('L')
    img = np.asarray(img)
    height, width = img.shape
   #////////////////////////////////////////////// Nearest neighbor algorithm////////////////////////


    # Apply Gaussian filter to smooth the image
    blur_radius = 1.0
    threshold = 50

    imgf = ndimage.gaussian_filter(img, blur_radius)

    # Apply thresholding to find connected components
    labeled, nr_objects = ndimage.label(imgf > threshold)
    print('number of objects',nr_objects)

    # Calculate GPS deltas per pixel
    lon_per_pixel = (lon2 - lon1) / width
    lat_per_pixel = (lat1 - lat2) / height

    output_directory = os.path.join('gps_output')

    # Extracting the filename without extension from the input image path
    output_image_filename = os.path.splitext(os.path.basename(image_file_path))[0] + '_gps.txt'

    # Creating the output path for the GPS text file
    output_path_gps = os.path.join(output_directory, output_image_filename)
    # Creating the directory for the output GPS text file if it doesn't exist
    os.makedirs(os.path.dirname(output_path_gps), exist_ok=True)


    gps_points = []
    data = []

    # Calculate bounding boxes, centers, widths, and heights for each object
    for i in range(1, nr_objects + 1):
        slice_y, slice_x = ndimage.find_objects(labeled == i)[0]
        x1, x2 = slice_x.start, slice_x.stop
        y1, y2 = slice_y.start, slice_y.stop

        width = x2 - x1
        height = y2 - y1

        if width > height:
            y_middle = (y1 + y2) // 2
            gps_start = pixel_to_gps(x1, y_middle)
            gps_end = pixel_to_gps(x2, y_middle)
            gps_points.append((gps_start, gps_end))
        else:
            x_middle = (x1 + x2) // 2
            gps_start = pixel_to_gps(x_middle, y1)
            gps_end = pixel_to_gps(x_middle, y2)
            gps_points.append((gps_start, gps_end))
        # Add the data to the list
            # Convert corner coordinates to GPS
        top_left_gps_corner = pixel_to_gps(x1, y1)
        top_right_gps_corner = pixel_to_gps(x2, y1)
        bottom_left_gps_corner = pixel_to_gps(x1, y2)
        bottom_right_gps_corner = pixel_to_gps(x2, y2)
        data.append({
            "id": i,
            "corners_pixel": {
                "top_left": {"x": x1, "y": y1},
                "top_right": {"x": x2, "y": y1},
                "bottom_left": {"x": x1, "y": y2},
                "bottom_right": {"x": x2, "y": y2}
            },
            "gps_coordinates": {
                "top_left": {"latitude": top_left_gps_corner[0], "longitude": top_left_gps_corner[1]},
                "top_right": {"latitude": top_right_gps_corner[0], "longitude": top_right_gps_corner[1]},
                "bottom_left": {"latitude": bottom_left_gps_corner[0], "longitude": bottom_left_gps_corner[1]},
                "bottom_right": {"latitude": bottom_right_gps_corner[0], "longitude": bottom_right_gps_corner[1]}
            }
        })
    with open('satellite/complete_gps_file.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Find the point with minimum latitude and minimum longitude
    upper_left_gps = (lat1, lon1)
    start_point = min(gps_points, key=lambda x: calculate_distance(upper_left_gps, x[0]))

    # Reorder GPS points using nearest neighbor algorithm starting from the minimum point
    ordered_gps_points = nearest_neighbor(gps_points, start_point)

    with open(output_path_gps, 'w') as gps_file:
        for i, (gps_start, gps_end) in enumerate(ordered_gps_points):
            if i % 2 == 0:  # If iteration is even, write end then start
                gps_file.write(f"{gps_start}, {gps_end}\n")

            else:  # If iteration is odd, write start and end
                gps_file.write(f"{gps_end}, {gps_start}\n")
    return output_image_filename






def waypoints_planning(input_image_path,start_lat,start_long,end_lat,end_long):
   label_file_path= segment_PV(input_image_path)
   output_gps_file=process_image(input_image_path,label_file_path,start_lat,start_long,end_lat,end_long)
   return output_gps_file

input_image_path='test.jpg'
start_lat=29.937424
start_long=  31.066178
29.937309, 31.066357
end_lat=29.937309
end_long=31.066357

#output_gps_file=waypoints_planning(input_image_path,start_lat,start_long,end_lat,end_long)
