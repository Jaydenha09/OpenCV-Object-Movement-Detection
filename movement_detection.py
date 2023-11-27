import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from datetime import datetime

print("Press q to quit the program\nPress t start the detection")
# Email configuration
SMTP_PORT = 587
SMTP_SERVER = 'email_server_address'
SENDER_EMAIL = 'the email address you want to send from'
SENDER_PASSWORD = 'smtp password'
RECIPIENT_EMAIL = 'the email you want to receive the notification'

cap = cv2.VideoCapture(0)  # Use camera index 0 for the default webcam

# Set the frame width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = cap.read()
start_frame = cv2.resize(start_frame, (500, 500))
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm_mode = False
alarm_counter = 0
alarm_stopped_sent = False
alarm_detected_sent = False


def send_email(subject, message, image_path='', image_bytes=''):

    if len(image_path):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg.attach(MIMEText(message))
        image = MIMEImage(image_bytes, name=image_path)
        msg.attach(image)
    else:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


def alarm_detected(image_path, image_bytes):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_email("Object Movement Detected", f"Object movement detected!\nTime: {current_time}", image_path, image_bytes)
    print(f"Movement Detected- Time: {current_time}")


def alarm_stopped():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_email("Object Movement Stopped", f"Object movement stopped!\nTime: {current_time}")
    print(f"Movement Stopped - Time: {current_time}")

def capture_imagee(frame):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f'captured_image_{current_time}.jpg'
    ret, image_buffer = cv2.imencode('.jpg', frame)
    image_bytes = image_buffer.tobytes()
    return image_path, image_bytes


while True:
    _, frame = cap.read()
    frame = cv2.resize(frame, (500, 500))

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

        difference = cv2.absdiff(frame_bw, start_frame)
        threshold = cv2.threshold(difference, 50, 255, cv2.THRESH_BINARY)[1] #sensitive setting example: threshold = cv2.threshold(difference, [value], 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        cv2.imshow("Cam", threshold)

        # print('threshold: {}, alarm_counter: {}, alarm_stopped_sent: {}, alarm_detected_sent: {}'.format(threshold, alarm_counter, alarm_stopped_sent, alarm_detected_sent))

        if threshold.sum() > 300:
            alarm_counter += 1
        elif alarm_counter > 0:
            alarm_counter -= alarm_counter / 10
            alarm_counter = int(alarm_counter)

        if alarm_counter == 0 and not alarm_stopped_sent:
            alarm_stopped_sent = True
            alarm_detected_sent = False
            alarm_stopped()
        elif alarm_counter > 20 and not alarm_detected_sent:
            alarm_detected_sent = True
            alarm_stopped_sent = False
            image_path, image_bytes = capture_imagee(frame)
            alarm_detected(image_path, image_bytes)
    else:
        cv2.imshow("Cam", frame)



    key_pressed = cv2.waitKey(30)
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    if key_pressed == ord("q"):
        alarm_mode = False
        break

cap.release()
cv2.destroyAllWindows()
