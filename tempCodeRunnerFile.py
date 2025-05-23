from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

# Text-to-Speech Function
def speak(str1):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(str1)

# Start Video Capture
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')

# Load Face Data
with open('Data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('Data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

# Train KNN Model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)
 
COL_NAMES = ['NAME', 'TIME']

while True:
    ret, frame = video.read()
    if not ret:
        print("Error: Camera not working!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)

        # Timestamp for Attendance
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        attendance_file = f"Attendance/Attendance_{date}.csv"

        # Draw Face Rectangle and Name
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        attendance = [str(output[0]), str(timestamp)]

    # Show Frame
    cv2.imshow("Frame", frame)

    k = cv2.waitKey(1)

    if k == ord('o'):  # If 'o' is pressed, take attendance
        speak("Attendance Taken.")
        time.sleep(1)

        # Save Attendance
        file_exists = os.path.isfile(attendance_file)
        with open(attendance_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(COL_NAMES)  # Write column names if file doesn't exist
            writer.writerow(attendance)

        break  # Exit after saving attendance

# Release Resources
video.release()
cv2.destroyAllWindows()
