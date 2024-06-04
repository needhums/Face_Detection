import os
import pickle
import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-50765-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-50765.appspot.com"
})
bucket = storage.bucket()

# Initialize the video capture object
cap = cv2.VideoCapture(0)

# Set the width and height of the video capture
cap.set(3, 1280)
cap.set(4, 720)

# Load the background image
background_path = 'Resources/background.png'
imgBackground = cv2.imread(background_path)

# Import mode images into list
folderModePath = 'Resources/modules'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList if path.endswith(('.png', '.jpg', '.jpeg'))]

# Import encoding file
print("Loading Encoded File...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentId = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    # Read a frame from the video capture
    success, img = cap.read()

    # Resize the input image
    img_resized = cv2.resize(img, (0, 0), None, 0.25, 0.25)

    # Convert to RGB color space
    imgs = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

    # Detect faces in the resized image
    faceCurFrame = face_recognition.face_locations(imgs)
    encodeCurFrame = face_recognition.face_encodings(imgs, faceCurFrame)

    # Check if the frame is read successfully
    if not success:
        print("Error: Failed to read frame.")
        break

    # Overlay the webcam feed onto the background image
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # Overlay the mode image onto the background image if imgModeList is not empty
    if imgModeList:
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    # Check if face is detected
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1

                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentId[matchIndex]

                # Update attendance for the recognized face
                if counter == 0:
                    studentInfo = db.reference(f'Students/{id}').get()

                    # Get the image from storage
                    blob = bucket.get_blob(f'Images/{id}.jpeg') or bucket.get_blob(f'Images/{id}.jpg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    # Update data of attendance
                    datetimeObject = datetime.strptime(studentInfo['Last_Attendance'], "%Y-%m-%d %H:%M:%S")
                    last_attendance_date = datetimeObject.date()
                    current_date = datetime.now().date()

                    # Check if the date of last attendance matches the current date
                    if current_date == last_attendance_date:
                        print("Your attendance is already marked")
                        break

                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total_Attendance'] += 1
                    ref.child('Total_Attendance').set(studentInfo['Total_Attendance'])
                    ref.child('Last_Attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    # Print current attendance
                    print(f"Attendance updated for {studentInfo['name']}. Total attendance: {studentInfo['Total_Attendance']}")

                if 10 < counter < 20:
                    modeType = 0

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['Total_Attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                    cv2.putText(imgBackground, str(studentInfo['name']), (974, 455),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                    cv2.putText(imgBackground, str(studentInfo['Major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                    cv2.putText(imgBackground, str(studentInfo['Starting_Year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    imgStudent_resized = cv2.resize(imgStudent, (216, 216))
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent_resized
                counter += 1
    else:
        # Reset counter and related variables if no face is detected
        counter = 0

        # Draw a rectangle on unauthorized person
        cv2.rectangle(imgBackground, (896, 408), (1139, 433), (128, 0, 128), cv2.FILLED)
        cv2.putText(imgBackground, 'Unauthorized person', (900, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Draw a circle with a cross inside
        cv2.circle(imgBackground, (1016, 305), 74, (0, 0, 0), cv2.FILLED)
        cv2.putText(imgBackground, 'X', (1016 - 10, 305 + 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    cv2.imshow("Face_Attendance", imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
