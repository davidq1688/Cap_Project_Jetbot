# -*- coding: utf-8 -*-
"""Copy of Counter and Capture camera. ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zzyLxJkb1posu7QpJrqIq66y_Dk4ETm9
"""

!pip install opencv-contrib-python
import cv2
import numpy as np
import matplotlib.pyplot as plt
# For Google Colab we use the cv2_imshow() function
from google.colab.patches import cv2_imshow

from IPython.display import display, Javascript
from google.colab.output import eval_js
from base64 import b64decode

def take_photo(filename='photo.jpg', quality=0.8):
  js = Javascript('''
    async function takePhoto(quality) {
      const div = document.createElement('div');
      const capture = document.createElement('button');
      capture.textContent = 'Capture';
      div.appendChild(capture);

      const video = document.createElement('video');
      video.style.display = 'block';
      const stream = await navigator.mediaDevices.getUserMedia({video: true});

      document.body.appendChild(div);
      div.appendChild(video);
      video.srcObject = stream;
      await video.play();

      // Resize the output to fit the video element.
      google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

      // Wait for Capture to be clicked.
      await new Promise((resolve) => capture.onclick = resolve);

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      stream.getVideoTracks()[0].stop();
      div.remove();
      return canvas.toDataURL('image/jpeg', quality);
    }
    ''')
  display(js)
  data = eval_js('takePhoto({})'.format(quality))
  binary = b64decode(data.split(',')[1])
  with open(filename, 'wb') as f:
    f.write(binary)
  return filename

from IPython.display import Image
try:
  filename = take_photo()
  print('Saved to {}'.format(filename))
  
  # Show the image which was just taken.
  display(Image(filename))
except Exception as err:
  # Errors will be thrown if the user does not have a webcam or if they do not
  # grant the page permission to access it.
  print(str(err))

from matplotlib import pyplot as plt
img = cv2.imread('/content/photo.jpg',0)
orig_image = img.copy()
img = cv2.medianBlur(img,5)
ret,th1 = cv2.threshold(img,170,255,cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(th1.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
plt.imshow(th1, cmap='gray')
print(len(contours))
for c in contours:
    x,y,w,h = cv2.boundingRect(c)
    plt.imshow(cv2.rectangle(th1,(x,y),(x+w,y+h),(100,100,255),10)    ) 
    plt.title('Bounding Rectangle');plt.show()
    print((x,y),(x,y+h),(x+w,y),(x+w,y+h))

