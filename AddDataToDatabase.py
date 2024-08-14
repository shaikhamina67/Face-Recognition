import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendance-65429-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "123232":
        {
            "name": "Phoebe",
            "major": "Actor",
            "starting_year":2017,
            "total_attendance":6,
            "standing":"A",
            "year":4,
            "last_attendance_time": "2024-04-27 00:54:34"
        },
    "222222":
        {
            "name": "Shaikh Amina",
            "major": "IT",
            "starting_year": 2017,
            "total_attendance": 2,
            "standing": "C",
            "year": 4,
            "last_attendance_time": "2024-04-27 00:54:34"
        },
    "387686":
        {
            "name": "Selena Gomez",
            "major": "Singer",
            "starting_year": 2017,
            "total_attendance": 8,
            "standing": "A",
            "year": 4,
            "last_attendance_time": "2024-04-27 00:54:34"
        },
    "966753":
        {
            "name": "Taylor Swift",
            "major": "Singer",
            "starting_year": 2017,
            "total_attendance": 0,
            "standing": "B",
            "year": 4,
            "last_attendance_time": "2024-04-27 00:54:34"
        }
}

for key,value in data.items():
    ref.child(key).set(value)

