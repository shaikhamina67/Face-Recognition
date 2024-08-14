import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendance-65429-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendance-65429.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3,342)
cap.set(4,268)

imgBackground = cv2.imread('resources/background.png')

# Importing the mode images into a list
folderModePath = 'resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[228:228 + 288, 41:41 + 352] = img
    imgBackground[49:49 + 500, 453:453 + 320] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("match Index", matchIndex)
            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 45 + x1, 225 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(130,350))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[49:49 + 500, 453:453 + 320] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[49:49 + 500, 453:453 + 320] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (510, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (600, 462), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 0), 1)
                    cv2.putText(imgBackground, str(id), (600, 414), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 0, 0), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (515, 526), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (610, 526), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (690, 526), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    offset = (320 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (455 + offset, 370), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (50, 50, 50), 2)

                    imgBackground[124:124 + 200, 512:512 + 200] = imgStudent

                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[49:49 + 500, 453:453 + 320] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("WebCam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
