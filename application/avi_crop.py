import cv2

def crop_video(input_video_path, output_video_path, crop_pixels=80):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Define the codec and create a VideoWriter object to save the cropped video
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height - crop_pixels))

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

    print(f"Cropped video saved to {output_video_path}")

# Usage example
input_video = 'application/input.avi'
output_video = 'application/outputt_video.avi'
crop_video(input_video, output_video)
