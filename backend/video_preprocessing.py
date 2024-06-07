

def get_video_resolution_frames(video_path):
    import ffmpeg
    import os
    import cv2
    from PIL import Image
    from moviepy.video.io.VideoFileClip import VideoFileClip

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    # Get the width and height of the video
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Release the video capture object
    cap.release()

    video = VideoFileClip(video_path)

    # Define the frame rate of the video
    total_frames = int(video.duration * video.fps)

    return int(width), int(height), total_frames


def detect_solar_module(input_video_path, project_dir, threshold=0.5):
    import ffmpeg
    import os
    import cv2
    from ultralytics import YOLO
    from PIL import Image

    # Initialize the YOLO model
    model = YOLO('best_vd.pt')

    # Open the video file
    video = cv2.VideoCapture(input_video_path)
    input_filename = os.path.splitext(os.path.basename(input_video_path))[0]
    # project_dir = "Modules_per_frame_5_right"
    labels_dir = os.path.join(project_dir, "labels", input_filename)
    frames_dir = os.path.join(project_dir, "frames", input_filename)

    # Create directories for saving results if they don't exist
    os.makedirs(labels_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    frame_count = 0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for saving video
    out = None

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        # Convert the frame to PIL Image
        frame_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Run inference on the frame
        results = model.predict(source=frame_image)

        # Initialize a list to store labels for this frame
        frame_labels = []

        # Draw bounding boxes on the frame and collect labels
        for box in results[0].boxes:
            conf = box.conf.item()  # Get confidence score
            if conf >= threshold:
                cls = box.cls.item()  # Get class label
                # Get bounding box coordinates in xyxy format
                xyxy = box.xyxy[0].tolist()

                # Draw bounding box
                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f'{cls}: {conf:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Append the label to the list for this frame
                frame_labels.append(f"{cls} {conf} {x1} {y1} {x2} {y2}")

        # Write all labels for this frame to the labels file
        frame_label_filename = f"{input_filename}_frame{frame_count:05d}.txt"
        frame_label_path = os.path.join(labels_dir, frame_label_filename)
        with open(frame_label_path, 'w') as label_file:
            for label in frame_labels:
                label_file.write(label + '\n')

        # Save the frame with bounding boxes
        frame_filename = f"{input_filename}_frame{frame_count:05d}.jpg"
        frame_path = os.path.join(frames_dir, frame_filename)
        cv2.imwrite(frame_path, frame)

        # Initialize the video writer
        if out is None:
            height, width, _ = frame.shape
            out = cv2.VideoWriter(os.path.join(project_dir, f'{input_filename}_output.mp4'), fourcc, video.get(
                cv2.CAP_PROP_FPS), (width, height))

        # Write the frame into the video file
        out.write(frame)

        frame_count += 1

    # Release the video capture and writer objects
    video.release()
    if out is not None:
        out.release()

    return labels_dir, frames_dir


def read_txt_files(folder_path):
    import ffmpeg
    import os
    import cv2
    from ultralytics import YOLO
    from PIL import Image
    # Initialize a dictionary to store the data from each file
    data_dict = {}

    # Loop through all the files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)

            # Read the file and process the lines
            with open(file_path, 'r') as file:
                lines = file.readlines()
                file_data = []

                for line in lines:
                    # Split each line into a list of numbers
                    numbers = line.strip().split()
                    # Convert the numbers to the appropriate type (float for confidence score, int for coordinates and class label)
                    class_label = float(numbers[0])
                    confidence_score = float(numbers[1])
                    x1 = int(numbers[2])
                    y1 = int(numbers[3])
                    x2 = int(numbers[4])
                    y2 = int(numbers[5])

                    # Append the list of 6 items to the file data
                    file_data.append(
                        [class_label, confidence_score, x1, y1, x2, y2])

                # Store the file data in the dictionary with the filename as the key
                data_dict[filename] = file_data

    return data_dict


def extract_x2_values(folder_path):
    import ffmpeg
    import os
    import cv2
    from ultralytics import YOLO
    from PIL import Image
    # Initialize a list to store x1 values from each file
    x2_values_list = []

    # Loop through all the files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)

            # Read the file and extract x1 values
            with open(file_path, 'r') as file:
                lines = file.readlines()
                x2_values = []

                for line in lines:
                    # Split each line into a list of numbers
                    numbers = line.strip().split()
                    # Convert x1 to integer and append to the list
                    x2 = int(numbers[4])
                    x2_values.append(x2)

                # Append the list of x1 values for this file to the main list
                x2_values_list.append(x2_values)

    return x2_values_list


def sort_x_values(x2_values_list):
    import ffmpeg
    import os
    import cv2
    from PIL import Image
    # Sort each list of x1 values
    for x2_values in x2_values_list:
        x2_values.sort()

    return x2_values_list


def extraction_left(x2_values, resolution):
    import ffmpeg
    import os
    import cv2
    from PIL import Image
    frames_indeses = []
    Cond_to_reach_frame_borders = resolution[
        0]
    sorted_x2_values = sort_x_values(x2_values)
    start_of_a_batch = 1
    lock = 0
    for frame_index, frame in enumerate(sorted_x2_values):
        if start_of_a_batch:
            if frame[-1] >= (Cond_to_reach_frame_borders-5):
                frames_indeses.append(frame_index)
            else:
                continue
            start_of_a_batch = 0

        else:
            n_of_modules = len(frame)
            if n_of_modules <= 1:
                continue

            if (abs(frame[-1]-frame[n_of_modules-2]) <= 5):
                if (lock == 0):
                    frames_indeses.append(frame_index)
                    lock = 1
            else:
                lock = 0
                continue
    return frames_indeses


def video_movement_direction_optimized(video_path, frame_skip=2, scale=0.5):
    import cv2
    import numpy as np
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)

    # Read the first frame
    ret, first_frame = cap.read()
    if not ret:
        print("Failed to read the video")
        cap.release()
        return None

    # Resize the first frame
    first_frame = cv2.resize(first_frame, (0, 0), fx=scale, fy=scale)

    # Convert the first frame to grayscale
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    # Initialize direction counters
    left_count, right_count, up_count, down_count = 0, 0, 0, 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1
        if not ret:
            break

        # Skip frames to reduce processing time
        if frame_count % frame_skip != 0:
            continue

        # Resize the frame
        frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Compute the average flow vector
        avg_flow = np.mean(flow, axis=(0, 1))

        # Determine direction based on the average flow vector
        if abs(avg_flow[0]) > abs(avg_flow[1]):  # Horizontal movement
            if avg_flow[0] > 0:
                right_count += 1
            else:
                left_count += 1
        else:  # Vertical movement
            if avg_flow[1] > 0:
                down_count += 1
            else:
                up_count += 1

        # Update the previous frame
        prev_gray = gray

    # Release the capture
    cap.release()

    # Determine the dominant direction
    directions = {'left': left_count, 'right': right_count,
                  'up': up_count, 'down': down_count}
    dominant_direction = max(directions, key=directions.get)

    return dominant_direction


def flip_video(input_path, output_path):
    from moviepy.editor import VideoFileClip, vfx
    """
    Flip the video vertically.

    :param input_path: Path to the input video file.
    :param output_path: Path to save the flipped video.
    """
    clip = VideoFileClip(input_path)
    flipped_clip = clip.fx(vfx.mirror_x)
    flipped_clip.write_videofile(
        output_path, codec='libx264', audio_codec='aac')


def rotate_90_left(input_path, output_path):
    from moviepy.editor import VideoFileClip, vfx
    """
    Rotate the video 90 degrees to the left (counter-clockwise).

    :param input_path: Path to the input video file.
    :param output_path: Path to save the rotated video.
    """
    clip = VideoFileClip(input_path)
    rotated_clip = clip.rotate(90)
    rotated_clip.write_videofile(
        output_path, codec='libx264', audio_codec='aac')


def rotate_90_right(input_path, output_path):
    from moviepy.editor import VideoFileClip, vfx
    """
    Rotate the video 90 degrees to the right (clockwise).

    :param input_path: Path to the input video file.
    :param output_path: Path to save the rotated video.
    """
    clip = VideoFileClip(input_path)
    rotated_clip = clip.rotate(-90)
    rotated_clip.write_videofile(
        output_path, codec='libx264', audio_codec='aac')


def save_cropped_frames(video_path, frames_indexes, x_start_points, output_dir):
    import cv2
    import os
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for i, frame_index in enumerate(frames_indexes):
        # Set the video capture to the specified frame index
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        ret, frame = cap.read()

        if not ret:
            print(f"Frame {frame_index} could not be read.")
            continue

        # Get the x-axis start point for cropping
        x_start = x_start_points[i]

        # Crop the frame from x_start to the end of the frame
        cropped_frame = frame[:, x_start:]

        # Save the cropped frame
        output_path = os.path.join(output_dir, f"frame_{frame_index}.png")
        cv2.imwrite(output_path, cropped_frame)
        print(f"Frame {frame_index} saved as {output_path}")

    # Release the video capture object
    cap.release()


def find_largest_and_second_largest(numbers):
    if len(numbers) < 2:
        return "List must contain at least two elements"

    # Initialize the largest and second largest with minimum possible values
    largest = second_largest = float('-inf')

    for number in numbers:
        if number > largest:
            # Update second largest before updating largest
            second_largest = largest
            largest = number
        elif number > second_largest and number != largest:
            second_largest = number

    if second_largest == float('-inf'):
        return "No second largest element found"

    return largest, second_largest


def get_starting_cutting_pixels(text_file_values, indeces):
    result_list = [[text_file_values[key]] for i, key in enumerate(text_file_values)]
    list_of_x1 = []
    
    for frame in indeces: 
        modules = result_list[frame]
        list_of_x2 = []
        list_of_areas = []
        
        for module in modules[0]:
            list_of_x2.append(module[4])
            list_of_areas.append((module[4]-module[2])*(module[5]-module[3]))
            
        largest, second_largest = find_largest_and_second_largest(list_of_x2)
        if largest - second_largest <= 10:
            n_1 = list_of_x2.index(largest)
            n_2 = list_of_x2.index(second_largest)

            if list_of_areas[n_1] > list_of_areas[n_2]:
                list_of_x1.append(n_1)
            else:
                list_of_x1.append(n_2)
        else:
            n_1 = list_of_x2.index(largest)
            list_of_x1.append(n_1)


    final_list = []
    for i, m in zip(indeces, list_of_x1):
        for j in result_list[i]:
            final_list.append(j[m][2])
            
    return final_list


def extraction(input_video_path, folder_path, output_dir):
    resolution = get_video_resolution_frames(input_video_path)
    direction = video_movement_direction_optimized(input_video_path)
    if direction == 'left':
        flip_video(input_video_path, 'flipped_output.mp4')
        labels_dir, _ = detect_solar_module(
            'flipped_output.mp4', folder_path)
        x2_values = extract_x2_values(labels_dir)
        text_file_values = read_txt_files(labels_dir)
        indeces = extraction_left(x2_values, resolution)
        starting_xs = get_starting_cutting_pixels(text_file_values, indeces)
        save_cropped_frames(input_video_path, indeces, starting_xs, output_dir)

    elif direction == 'right':
        labels_dir, _ = detect_solar_module(input_video_path, folder_path)
        x2_values = extract_x2_values(labels_dir)
        text_file_values = read_txt_files(labels_dir)
        indeces = extraction_left(x2_values, resolution)
        starting_xs = get_starting_cutting_pixels(text_file_values, indeces)
        save_cropped_frames(input_video_path, indeces, starting_xs, output_dir)

    elif direction == 'up':
        rotate_90_right(input_video_path, 'rotated_right_output.mp4')
        labels_dir, _ = detect_solar_module(
            'rotated_right_output.mp4', folder_path)
        x2_values = extract_x2_values(labels_dir)
        text_file_values = read_txt_files(labels_dir)
        indeces = extraction_left(x2_values, resolution)
        starting_xs = get_starting_cutting_pixels(text_file_values, indeces)
        save_cropped_frames(input_video_path, indeces, starting_xs, output_dir)

    elif direction == 'down':
        rotate_90_left(input_video_path, 'rotated_left_output.mp4')
        labels_dir, _ = detect_solar_module(
            'rotated_left_output.mp4', folder_path)
        x2_values = extract_x2_values(labels_dir)
        text_file_values = read_txt_files(labels_dir)
        indeces = extraction_left(x2_values, resolution)
        starting_xs = get_starting_cutting_pixels(text_file_values, indeces)
        save_cropped_frames(input_video_path, indeces, starting_xs, output_dir)

 
#######################################################################################
#                                      Testing                                        #
#######################################################################################

folder_path = r's_m_10'
output_dir = "output_frames_10"

#extraction(input_file_right, folder_path, resolution, output_dir)