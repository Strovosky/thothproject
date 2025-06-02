import datetime


date_imaginary = datetime.datetime(2025, 3, 25)

if date_imaginary < datetime.datetime.now():
    print(type(date_imaginary), type(datetime.datetime.now()))
    print("Yes, it is less")

