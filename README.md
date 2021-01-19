# thai-ocr-reader

An OCR output reader for images in Thai.

~~ Written by safe and jay ~~

Hello! This API, in its current state, gathers bounding box information from a
set of images which has been pre-processed through tesseract-ocr. The images are
hosted on Cloudinary, and each one is processed individually.

When sending a GET request to the main route, it will return the following
fields:

secure_url = image url on cloudinary
char = information by characters
word = information by word
  b = full set of information
  [x, y, w , h] = bounding box coordinates 
