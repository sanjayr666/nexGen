from PIL import Image
import pytesseract as pt
import cv2

im  = Image.open("sample.png")
text = pt.image_to_string(im,lang='eng')

print(text)
