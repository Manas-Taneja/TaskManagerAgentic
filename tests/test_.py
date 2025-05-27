import smtplib

EMAIL = "manas53tan@gmail.com"
PASSWORD = "quxxkmokhpdigrqm"  # No quotes, no spaces

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    print("Login succeeded!")
except Exception as e:
    print("Login failed:", e)
