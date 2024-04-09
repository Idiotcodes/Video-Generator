# import necessary libraries
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import io
from PIL import Image
from gtts import gTTS
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips

# load api keys
load_dotenv()

# set the api keys
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
hug_api_key = os.environ.get("HUG_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": f"Bearer {hug_api_key}"}

# let's initialize model to get inference from the image
llm = ChatGoogleGenerativeAI(model="gemini-pro-vision",
                             google_api_key=GOOGLE_API_KEY,
                             max_output_tokens=100)


#let's define function to detect object from the image
def detect_object(img_path):
  message = HumanMessage(content=[
      {
          "type":
          "text",
          "text":
          "detect the object in the image, just retun the detected objects name, for example if it's a laptop return laptop, don't make thinks up"
      },  # You can optionally provide text parts
      {
          "type": "image_url",
          "image_url": img_path
      },
  ])
  response = llm.invoke([message])
  return response.content


# let's define a function to get inference from the image
def get_inference(img_path):
  message = HumanMessage(content=[
      {
          "type": "text",
          "text": "what's in this image, give a short detail on the image"
      },  # You can optionally provide text parts
      {
          "type": "image_url",
          "image_url": img_path
      },
  ])
  response = llm.invoke([message])
  return response.content


# let's define some paths
output_path = os.path.join('static', 'output')
image_save_path = os.path.join(output_path, 'gen_image1.jpg')
image1_save_path = os.path.join(output_path, 'gen_image2.jpg')
image2_save_path = os.path.join(output_path, 'gen_image3.jpg')
audio_save_path = os.path.join(output_path, 'gen_audio.mp3')
video_save_path = os.path.join(output_path, 'gen_video.mp4')


# let's define a function to generate image from response
def query(payload):
  response = requests.post(API_URL, headers=headers, json=payload)
  return response.content


def generate_image(detect_object):

  image_bytes = query({
      "inputs": detect_object,
  })
  image = Image.open(io.BytesIO(image_bytes))
  image.save(image_save_path)

  # for second image
  image_bytes = query({
      "inputs": f'dramatic,{detect_object}',
  })
  image1 = Image.open(io.BytesIO(image_bytes))
  image1.save(image1_save_path)

  # for third image
  image_bytes = query({
      "inputs": f'A photorealistic,{detect_object}',
  })
  image1 = Image.open(io.BytesIO(image_bytes))
  image1.save(image2_save_path)


# let's define function to convert text to speech
def generate_audio(object_description):
  tts = gTTS(object_description, lang='en')
  tts.save(audio_save_path)


# let's define function for getting video
def generate_video():
  # Load audio
  audio = AudioFileClip(audio_save_path)
  # Split audio
  avg_duration = audio.duration / 3
  audio1 = audio.subclip(0, avg_duration)
  audio2 = audio.subclip(avg_duration, 2 * avg_duration)
  audio3 = audio.subclip(2 * avg_duration, audio.duration)
  # Load images
  image1 = ImageSequenceClip([image_save_path],
                             durations=[audio1.duration
                                        ])  # Set duration for each image
  image2 = ImageSequenceClip([image1_save_path], durations=[audio2.duration])
  image3 = ImageSequenceClip([image2_save_path], durations=[audio3.duration])
  # Combine images
  final_clip = concatenate_videoclips([image1, image2, image3],
                                      method="compose")
  # Set audio to video clips
  final_clip = final_clip.set_audio(audio)
  # Write the final video with the first half of the audio
  final_clip.write_videofile(video_save_path, fps=1)
  return video_save_path
  


