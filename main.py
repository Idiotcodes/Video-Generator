from flask import Flask, render_template, request, send_from_directory, redirect
from werkzeug.utils import secure_filename
import os
from helper import detect_object, get_inference, generate_image, generate_audio, generate_video, generate_video_from_text

app = Flask(__name__)

# Configure allowed upload extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# Function to check allowed file extensions
def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/text-to-video', methods=['GET', 'POST'])
def text_to_video():
    if request.method == 'POST':
        # Get the text data from the request (similar to getting image data)
        text_data = request.form['textInput']  # Assuming the text input has id "textInput"

        # Process the text data (similar to processing image data)
        object_description = text_data  # Use the text as the description
        generate_image(object_description)
        generate_audio(object_description)
        video_save_path = generate_video()
        return redirect("/textvideoplayer") 

        # Send the generated video to the user
        return send_from_directory(os.path.dirname(video_save_path),
                                   os.path.basename(video_save_path))

    return render_template('text-to-video.html')
  
@app.route('/image-to-video', methods=['GET', 'POST'])
def image_to_video():
  if request.method == 'POST':
    # Check if the post request has the file part
    if 'file' not in request.files:
      return "No file part"
    file = request.files['file']
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      return "No selected file"
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file_path = os.path.join(app.static_folder, 'uploads', filename)
      file.save(file_path)
      # Process image with AI functions
      object_detected = detect_object(file_path)
      object_description = get_inference(file_path)

      # Save detected objects to gen_keyword.txt
      keywords_file_path = os.path.join(app.static_folder, 'output', 'gen_keyword.txt')
      with open(keywords_file_path, 'w') as f:
          for obj in object_detected:  # Assuming object_detected is a list of objects
              f.write(obj)

      description_file_path = os.path.join(app.static_folder, 'output', 'gen_desc.txt')
      with open(description_file_path, 'w') as f:
          for obj in object_description:  # Assuming object_detected is a list of objects
              f.write(obj)
            
      generate_image(object_description)
      generate_audio(object_description)
      video_save_path = generate_video()
      return redirect("/imgvideoplayer") 
      # Send generated video to user
      return send_from_directory(os.path.dirname(video_save_path),
                                 os.path.basename(video_save_path))
  return render_template('image-to-video.html')



@app.route('/imgvideoplayer')
def imgplayer():
    # Read detected keywords from gen_keywords.txt
    keywords_file_path = os.path.join(app.static_folder, 'output', 'gen_keyword.txt')
    try:
        with open(keywords_file_path, 'r') as f:
            object_detected = f.read()  # Read lines and remove newlines
    except FileNotFoundError:
        object_detected = [] 

    description_file_path = os.path.join(app.static_folder, 'output', 'gen_desc.txt')
    try:
        with open(description_file_path, 'r') as f:
            object_description = f.read()  # Read lines and remove newlines
    except FileNotFoundError:
        object_description = [] 
# Set an empty list if file not found

    # ... (Assuming you have a way to get object_description, 
    #     or you can set it to None or an empty string if not needed) ... 

    return render_template('imgvideoplayer.html', 
                           object_detected=object_detected, 
                           object_description=object_description)

@app.route('/textvideoplayer')
def textplayer():
  return render_template('textvideoplayer.html')
# (Optional) Add route for text-to-video if needed

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
