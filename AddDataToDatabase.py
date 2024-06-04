import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL':"https://faceattendance-50765-default-rtdb.firebaseio.com/"})

ref=db.reference('Students')
data={
    '101':
        {
            "name":"Ajai Krishna",
            "Major":"Data_Science",
            "Starting_Year":2023,
            "Total_Attendance":10,
            "Last_Attendance":"2024-04-22 00:54:55"
        },
    '102':
        {
            "name": "Emma Watson",
            "Major": "Python",
            "Starting_Year": 2023,
            "Total_Attendance": 8,
            "Last_Attendance": "2024-04-22 00:34:55"
        },
    '103':
        {
            "name": "Paul Walker",
            "Major": "Data_Science",
            "Starting_Year": 2023,
            "Total_Attendance": 10,
            "Last_Attendance": "2024-04-22 00:22:22"
        },
    '104':
        {
            "name": "M S Needhu",
            "Major": "Data Science",
            "Starting_Year": 2023,
            "Total_Attendance": 0,
            "Last_Attendance": "2024-04-10 00:44:00"
        },
    '105':
        {
            "name": "Tony Stark",
            "Major": "Data_Science",
            "Starting_Year": 2023,
            "Total_Attendance": 10,
            "Last_Attendance": "2024-04-01 00:30:22"
        },
    '106' and '107':
        {
            "name": "Akhosh V S",
            "Major": "Data_Science",
            "Starting_Year": 2023,
            "Total_Attendance": 10,
            "Last_Attendance": "2024-04-01 00:30:22"
        }
}

for key,value in data.items():
    ref.child(key).set(value)