import numpy as np
import cv2

def fahrenheit2celcius(f):
    return (f - 32) * 5 / 9

# hangi fotoğrafın üzerinde çalışacağız
name = "IR_00265"
# csv dosyasının ismini oluşturalım
csv_file = f'temperature/{name}{".csv"}'
# Fluke Thermal Imager tarafından bize sağlanan sıcaklık haritası 240x320 CCD boyutunda
temperature = np.genfromtxt(csv_file, dtype=np.float64, delimiter=',', skip_header=5, encoding="utf16")
temperature = temperature[:,1:-1]
print(temperature.shape)
print(temperature.dtype)
print(temperature)
############### Derin Öğrenme ile Yüz Tespiti (Face Detection with Deep Learning) #####################
# load our serialized model from disk
print("[BİLGİ] derin öğrenme modeli yükleniyor...")
# dnn deep neural network
net = cv2.dnn.readNetFromCaffe('deploy.prototxt.txt', 'res10_300x300_ssd_iter_140000.caffemodel')
conf = 0.5 # minimum probability to filter weak detections
# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
img_name, img_extension = f"{name}_RGB", "png"
infrared_img_name, infrared_img_extension = name, "png"
img_rgb = cv2.imread(f'image/{img_name}.{img_extension}')
img_infrared = cv2.imread(f'image/{infrared_img_name}.{infrared_img_extension}')
img_infrared_clone = img_infrared.copy()
# save output image as 320 x 240 as thermal matrix is at this size.
# This means Fluke thermal imager CCD is 320 x 240. Yet Fluke can give output up to 5mp by interpolation.
img_thermal_imager_ccd = cv2.resize(img_infrared_clone, (320,240), cv2.INTER_LINEAR)
img_rgb_ccd = cv2.resize(img_rgb, (320,240), cv2.INTER_LINEAR)
# cv2.imwrite(f"result/{img_name}_CCD.jpg", img_rgb_ccd, [cv2.IMWRITE_JPEG_QUALITY, 100])
cv2.imwrite(f"result/{infrared_img_name}_thermal_imager_CCD.jpg", img_thermal_imager_ccd, [cv2.IMWRITE_JPEG_QUALITY, 100])

# face detection with DL on CCD image
(h, w) = img_rgb_ccd.shape[:2]
blob = cv2.dnn.blobFromImage(cv2.resize(img_rgb_ccd, (300, 300)), 1.0,
	(300, 300), (104.0, 177.0, 123.0))

# pass the blob through the network and obtain the detections and predictions
print("[INFO] computing object detections...")
net.setInput(blob)
detections = net.forward()

max_temperature = []
threshold_temperature = 35
# loop over the detections
for i in range(0, detections.shape[2]):
	# extract the confidence (i.e., probability) associated with the
	# prediction
	confidence = detections[0, 0, i, 2]

	# filter out weak detections by ensuring the `confidence` is greater than the minimum confidence
	if confidence > conf:
		# compute the (x, y)-coordinates of the bounding box for the object
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")
		# extract the face region in temperature data
		ROI = temperature[startY:endY,startX:endX]
		# find the max temperature in the face region
		max_temperature.append(fahrenheit2celcius(np.max(ROI)))
		text = f"{max_temperature[i]:.2f} C"
		y = startY - 10 if startY - 10 > 10 else startY + 10
		BLACK, WHITE = (0, 0, 0), (255, 255, 255)
		cv2.rectangle(img_thermal_imager_ccd, (startX, startY), (endX, endY), WHITE, 2)
		cv2.putText(img_thermal_imager_ccd, text, (startX+1, y-1), 0, 0.5, WHITE, 1)
		cv2.circle(img_thermal_imager_ccd, (startX+50,startY-20), 2, WHITE, 1, 0)
# save output image
cv2.imwrite(f"result/{infrared_img_name}_thermal_imager_face_detection_CCD.jpg", img_thermal_imager_ccd, [cv2.IMWRITE_JPEG_QUALITY, 100])

# show the output image
cv2.imshow("Face & Fever Detection on CCD image", img_thermal_imager_ccd)

# face detection with DL on 5mp image, this is for Adem's thesis, better pictures
(h, w) = img_rgb.shape[:2]
blob = cv2.dnn.blobFromImage(cv2.resize(img_rgb, (300, 300)), 1.0,
	(300, 300), (104.0, 177.0, 123.0))

# pass the blob through the network and obtain the detections and predictions
print("[INFO] computing object detections...")
net.setInput(blob)
detections = net.forward()

# loop over the detections
for i in range(0, detections.shape[2]):
	# extract the confidence (i.e., probability) associated with the
	# prediction
	confidence = detections[0, 0, i, 2]

	# filter out weak detections by ensuring the `confidence` is
	# greater than the minimum confidence
	if confidence > conf:
		# compute the (x, y)-coordinates of the bounding box for the object
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")
		# draw the bounding box of the face along with the associated probability
		text = f"{max_temperature[i]:.2f} C"
		y = startY - 10 if startY - 10 > 10 else startY + 10
		BLACK = (0, 0, 0)
		GREEN = (0, 255, 0)
		cv2.rectangle(img_rgb, (startX, startY), (endX, endY), GREEN, 6)
		cv2.rectangle(img_infrared, (startX, startY), (endX, endY), WHITE, 6)
		cv2.putText(img_infrared, text, (startX+5, y-15), 0, 1.5, WHITE, 3)
		cv2.circle(img_infrared, (startX+150,startY-55), 5, WHITE, 4, 0)
		if max_temperature[i] > threshold_temperature:
			cv2.putText(img_infrared, "Fever detection!", (startX-75, y-65), 0, 1.5, WHITE, 3)
# save output image
cv2.imwrite(f"result/{infrared_img_name}_fever_detection.jpg", img_infrared, [cv2.IMWRITE_JPEG_QUALITY, 100])
cv2.imwrite(f"result/{img_name}_face_detection.jpg", img_rgb, [cv2.IMWRITE_JPEG_QUALITY, 100])
# show the output image
s = 0.5
rimage = cv2.resize(img_infrared, (int(s*img_infrared.shape[1]), 
												 int(s*img_infrared.shape[0])), cv2.INTER_LINEAR)
cv2.imshow("Face & fever detection on 5mp image", rimage)
cv2.waitKey(0)