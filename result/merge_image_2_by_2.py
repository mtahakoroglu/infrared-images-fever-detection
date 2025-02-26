import cv2
import numpy as np

name = "IR_00121"
img1name = f"./../image/{name}_RGB.png"
img2name = f"./../image/{name}.png"
img3name = f"{name}_RGB_face_detection.jpg"
img4name = f"{name}_fever_detection.jpg"
img1 = cv2.imread(img1name)
img2 = cv2.imread(img2name)
img3 = cv2.imread(img3name)
img4 = cv2.imread(img4name)

img1name, img1Extension = img1name.rsplit('.', 1)
img2name, img2Extension = img2name.rsplit('.', 1)
img3name, img3Extension = img3name.rsplit('.', 1)
img4name, img4Extension = img4name.rsplit('.', 1)
imgName, k = "", 0
while True:
    if img3name[k] == img4name[k]:
        imgName = f"{imgName}{img3name[k]}"
        k = k+1
    else:
        imgName = imgName[0:-1] # drop the last letter that is _
        break

h, w, c = img1.shape
# insert (a) (b) (c) (d) on upper right of the images
if w == 1280:
    xshift, yshift, fontType, fontScale, color, thickness = 150, 100, 0, 2, (255,255,255), 6
elif w == 640:
    xshift, yshift, fontType, fontScale, color, thickness = 60, 50, 0, 1, (255,255,255), 3
img1 = cv2.putText(img1, "(a)", (w-xshift, yshift), fontType, fontScale, color, thickness, 0)
img2 = cv2.putText(img2, "(b)", (w-xshift, yshift), fontType, fontScale, color, thickness, 0)
img3 = cv2.putText(img3, "(c)", (w-xshift, yshift), fontType, fontScale, color, thickness, 0)
img4 = cv2.putText(img4, "(d)", (w-xshift, yshift), fontType, fontScale, color, thickness, 0)
# combine all images to show the result as a single image
img = np.zeros((2*h, 2*w, c), np.uint8)
img[0:h,0:w,:] = img1
img[0:h,w:2*w,:] = img2
img[h:2*h,0:w,:] = img3
img[h:2*h,w:2*w,:] = img4

# resize image to display on screen
s = 0.5
rimg = cv2.resize(img, (int(s*img.shape[1]), int(s*img.shape[0])), 0)
cv2.imshow("Merged image", rimg)
cv2.waitKey(0)
# save image
cv2.imwrite(f"{imgName}_RGB_infrared_faces_fever.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 50])