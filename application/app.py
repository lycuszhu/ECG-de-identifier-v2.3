from flask import Flask, request, render_template, redirect, url_for, send_file, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import zipfile
import shutil
import deiden_new as deiden_new
from werkzeug import Request
import time
import pydicom
import cv2

Request.max_form_parts = 50000  # or whatever your max form size!

ALLOWED_EXTENSIONS = {'txt', 'xml','XML'}
folder_name = ""
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    input_folder = os.path.abspath("input")
    output_folder = os.path.abspath("output")
    echo_folder = os.path.abspath("echo")
    avi_folder = os.path.abspath('avi_temp')
    raw_folder = os.path.abspath('raw_temp')

    print(avi_folder)

    # Helper function to delete all files in a folder
    def delete_files(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    # Delete all files in the output folder when the app launches
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(avi_folder, exist_ok=True)
    os.makedirs(raw_folder, exist_ok=True)
    os.makedirs(echo_folder, exist_ok=True)

    delete_files(input_folder)
    delete_files(output_folder)
    delete_files(echo_folder)
    delete_files(avi_folder)
    delete_files(raw_folder)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        global folder_name
        delete_files(input_folder)
        delete_files(output_folder)
        delete_files(echo_folder)
        delete_files(avi_folder)
        delete_files(raw_folder)
        if request.method == 'POST':
            files = request.files.getlist('file')
            print(f'Number of Files Detected: {len(files)}')
            print(files)

            first_file = files[0]
            folder_path = os.path.dirname(first_file.filename)  # Relative folder path
            folder_name = os.path.basename(folder_path)  # Folder name

            print(f"Folder Name: {folder_name}")
            print(f"Number of Files: {len(files)}")

            if not files:
                return "No files selected", 400

            os.makedirs(input_folder, exist_ok=True)
            os.makedirs(output_folder, exist_ok=True)
            file_counters = {"philips": 0, "mindray": 0, "mortara": 0}

            for file in files:
                if file and allowed_file(file.filename):
                    base_filename = os.path.basename(file.filename)
                    print(f'Original filename: {file.filename}')
                    print(f'Base filename: {base_filename}')

                    # Secure the base filename
                    filename = secure_filename(base_filename)
                    print(f'Secure filename: {filename}')
                    new_filename = f'{filename.rsplit(".", 1)[0]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.XML'
                    print(f'new filename: {new_filename}')

                    file.save(os.path.join(input_folder, filename))

            return redirect(url_for('progress'))

        return render_template('upload.html')

    @app.route('/progress', methods=['GET', 'POST'])
    def progress():
        return render_template('progress.html')
    
    @app.route('/process_files')
    def process_files():
        def generate():
            global folder_name
            print("Starting Process_Files")
            file_counters = {"philips": 0, "mindray": 0, "mortara": 0}

            total_files = len([f for f in os.listdir(input_folder) if f.endswith(('.txt', '.xml','.XML'))])
            processed_files = 0

            for filename in os.listdir(input_folder):
                print("Listing files with devices")
                if filename.endswith(('.txt', '.xml','.XML')):
                    file_path = os.path.join(input_folder, filename)
                    print(f'file_path{file_path}')
                    #output_path = os.path.join(output_folder, filename)
                    # output_path = os.path.join(output_folder)
                    device_name = deiden_new.detect_type.detect_device_type(file_path)
                    device_name = device_name.lower()
                    print(device_name)
                    file_counters[device_name] += 1
                    print(f'Device Enlisting Completed with the dictionary: {file_counters}')

            for filename in os.listdir(input_folder):
                print("Checking filename")
                if filename.endswith(('.txt', '.xml','.XML')):
                    file_path = os.path.join(input_folder, filename)
                    print(f'file_path{file_path}')
                    #output_path = os.path.join(output_folder, filename)
                    output_path = os.path.join(output_folder)
                    # file_counters[device_name] += 1

                    # Process the file
                    device_name = deiden_new.detect_type.detect_device_type(file_path)
                    if device_name.lower() == 'mindray':
                        # output_path_name = device_name.lower()
                        print(f'folder_name in the path: {folder_name}')
                        filename_ = folder_name + "_" + device_name.lower()+"_"+str(file_counters[device_name.lower()])
                        file_counters[device_name.lower()] -= 1

                        print(filename_)
                        deiden_new.process_mindray_file(filename_, file_path, output_path)
                        print(device_name)
                    elif device_name.lower() == 'philips':
                        filename_ = folder_name + "_" + device_name.lower()+"_"+str(file_counters[device_name.lower()])
                        file_counters[device_name.lower()] -= 1

                        print(filename_)

                        deiden_new.process_philips_file(filename_, file_path, output_path)
                        print(device_name)
                    elif device_name.lower() == 'mortara':
                        filename_ = folder_name + "_" + device_name.lower()+"_"+str(file_counters[device_name.lower()])
                        file_counters[device_name.lower()] -= 1

                        print(filename_)

                        deiden_new.process_mortara_file(filename_, file_path, output_path)
                        print(device_name)

                    else:
                        print(f"Unknown device name: {device_name}")


                    print ([(key, file_counters[key]) for key in file_counters]) #printing the remaining ones
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    yield f"data:{progress}\n\n"

            # Create the ZIP file
            zip_filename = f"ecg_deidentified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_filepath = os.path.join(output_folder, zip_filename)
            print(f'Creating zip from the folder {zip_filepath}')
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for root, dirs, files in os.walk(output_folder):
                    for file in files:
                        if file != zip_filename:
                            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_folder))

            yield f"data:complete:{zip_filename}\n\n"

        return Response(generate(), mimetype='text/event-stream')





    @app.route('/download_file/<filename>', methods=['GET', 'POST'])
    def download_file(filename):
        file_path = os.path.join(output_folder, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return "File not found", 404
    
    @app.route('/download_page/<filename>', methods=['GET', 'POST'])
    def download_page(filename):
        return render_template('download.html', filename=filename)



    @app.route('/echo', methods=['GET', 'POST'])
    def echo_conversion():
        if request.method == 'POST':
            files = request.files.getlist('files')
            if not files:
                return "No files selected", 400

            os.makedirs(echo_folder, exist_ok=True)
            os.makedirs(avi_folder, exist_ok=True)
            delete_files(avi_folder)
            os.makedirs(raw_folder, exist_ok=True)
            delete_files(raw_folder)

            file_type = request.form.get('output_format')
            print(f'file type = {file_type}')

            if file_type == "avi":
                for file in files:
                    # Extract just the filename part from the path
                    original_filename = file.filename
                    filename = os.path.basename(original_filename)
                    
                    # Sanitize the filename
                    sanitized_filename = secure_filename(filename)
                    
                    print(f'Original filename: {original_filename}')
                    print(f'Sanitized filename: {sanitized_filename}')
                    
                    # Define the path where the file will be saved
                    dicom_path = os.path.join(echo_folder, sanitized_filename)
                    
                    # Save the file
                    file.save(dicom_path)
                    
                    print(f"Saved file to: {dicom_path}")

                    try:
                        # dicom_data = pydicom.dcmread(dicom_path)

                        cap = cv2.VideoCapture(dicom_path)

                        # Get video properties
                        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                        # Define the codec and create a VideoWriter object to save the cropped video
                        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                        crop_pixels = 80
                        video_filename = os.path.join(avi_folder, f'{filename}.avi')                        
                        out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height - crop_pixels))

                        frame_count = 0
                        while cap.isOpened():
                            ret, frame = cap.read()
                            if not ret:
                                break
                            
                            # Crop the frame (remove 80 pixels from the top)
                            cropped_frame = frame[crop_pixels:, :]

                            # Write the cropped frame to the output video
                            out.write(cropped_frame)

                            frame_count += 1
                            print(f"Processed frame {frame_count}/{total_frames}")

                        # Release the video objects
                        cap.release()
                        out.release()

                        print(f"Cropped video saved to {video_filename}")

                        # number_of_frames = dicom_data.get("NumberOfFrames", 1)
                        # if isinstance(number_of_frames, pydicom.valuerep.DSfloat):
                        #     number_of_frames = int(number_of_frames)

                        # pixel_data = dicom_data.pixel_array
                        # pixel_data = pixel_data[:, 80:, :, :]

                        # frame_time = dicom_data.get('FrameTime', 40)
                        # if isinstance(frame_time, (pydicom.valuerep.DSfloat, str)):
                        #     frame_time = float(frame_time)
                        # fps = 1000 / frame_time

                        # frame_shape = pixel_data[0].shape if number_of_frames > 1 else pixel_data.shape
                        # frame_size = (224, 224)

                        # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                        # video_filename = os.path.join(avi_folder, f'{filename}.avi')
                        # video_writer = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)

                        # if number_of_frames > 1:
                        #     for frame_index in range(number_of_frames):
                        #         frame = pixel_data[frame_index]
                        #         if len(frame.shape) == 2:
                        #             frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        #         elif frame.shape[2] == 3:
                        #             frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        #         frame_rescaled = cv2.resize(frame, frame_size)
                        #         video_writer.write(frame_rescaled)
                        # else:
                        #     frame = pixel_data
                        #     if len(frame.shape) == 2:
                        #         frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                        #     elif frame.shape[2] == 3:
                        #         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        #     frame_rescaled = cv2.resize(frame, frame_size)
                        #     video_writer.write(frame_rescaled)

                        # video_writer.release()

                    except Exception as e:
                        print(f"Error processing {dicom_path}: {e}")
                        return f"Error processing DICOM file: {e}", 500

                zip_filename = f"echo_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                zip_filepath = os.path.join(avi_folder, zip_filename)
                print(f"Creating ZIP file: {zip_filepath}")
                with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                    for root, dirs, files in os.walk(avi_folder):
                        for file in files:
                            if file != zip_filename:
                                file_path = os.path.join(root, file)
                                zipf.write(file_path, os.path.relpath(file_path, avi_folder))
                                print(f"Added to ZIP: {file_path}")

                print(f"Sending ZIP file for avi: {zip_filepath}")
                return render_template('download_echo.html', zip_filename=zip_filename)

            elif file_type == "raw":
                def process_dicom_files(files, echo_folder, raw_folder):
                    for file in files:


                        original_filename = file.filename
                        filename = os.path.basename(original_filename)
                        
                        # Sanitize the filename
                        sanitized_filename = secure_filename(filename)
                        
                        print(f'Original filename: {original_filename}')
                        print(f'Sanitized filename: {sanitized_filename}')
                        
                        # Define the path where the file will be saved
                        dicom_path = os.path.join(echo_folder, sanitized_filename)
                        raw_path = os.path.join(raw_folder, filename)

                        # Save the file
                        file.save(dicom_path)
                        
                        print(f"Saved file to: {dicom_path}")


                        # filename = secure_filename(file.filename)
                        # dicom_path = os.path.join(echo_folder, filename)
                        # raw_path = os.path.join(raw_folder, filename)
                        # file.save(dicom_path)
                        # print(f"Saved file: {dicom_path}")

                        try:
                            dicom_data = pydicom.dcmread(dicom_path)

                            number_of_frames = dicom_data.get("NumberOfFrames", 1)
                            if isinstance(number_of_frames, pydicom.valuerep.DSfloat):
                                number_of_frames = int(number_of_frames)

                            pixel_data = dicom_data.pixel_array

                            # Slice the pixel data to exclude the first 80 pixels
                            sliced_pixel_data = pixel_data[:, 80:, :, :]

                            # Update the PixelData attribute with the sliced pixel array
                            if dicom_data.file_meta.TransferSyntaxUID.is_compressed:
                                print(f"Error: Compressed data handling is not yet implemented")
                            else:
                                dicom_data.PixelData = sliced_pixel_data.tobytes()
                                dicom_data.Rows = sliced_pixel_data.shape[1]
                                dicom_data.Columns = sliced_pixel_data.shape[2]

                            # Save the modified DICOM file
                            dicom_data.save_as(raw_path)
                            print(f"Processed and saved file: {raw_path}")

                        except Exception as e:
                            print(f"Error processing file {dicom_path}: {e}")

                process_dicom_files(files, echo_folder, raw_folder)

                zip_filename = f"echo_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                zip_filepath = os.path.join(raw_folder, zip_filename)
                print(f"Creating ZIP file: {zip_filepath}")
                with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                    for root, dirs, files in os.walk(raw_folder):
                        for file in files:
                            if file != zip_filename:
                                file_path = os.path.join(root, file)
                                zipf.write(file_path, os.path.relpath(file_path, raw_folder))
                                print(f"Added to ZIP: {file_path}")

                print(f"Sending ZIP file: {zip_filepath}")
                return render_template('download_raw.html', zip_filename=zip_filename)

        return render_template('echo.html')

    @app.route('/download_echo/<filename>')
    def download_echo_file(filename):
        file_path = os.path.join(avi_folder, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, mimetype='application/zip')
        return "File not found", 404

    # @app.route('/download_echo/<filename>')
    # def download_echo_file(filename):
    #     file_path = os.path.join(avi_folder, filename)
    #     if os.path.exists(file_path):
    #         return send_file(file_path, as_attachment=True, mimetype='application/zip')
    #     return "File not found", 404

    @app.route('/download_raw/<filename>')
    def download_raw_file(filename):
        file_path = os.path.join(raw_folder, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, mimetype='application/zip')
        return "File not found", 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
