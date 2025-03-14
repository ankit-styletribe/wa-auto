import time
import urllib.parse
import threading
import queue
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# ----------------------------
# Selenium and Browser Setup
# ----------------------------
canary_path = "C:\\Users\\ankit\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe"
chromedriver_path = "C:\\Users\\ankit\\Desktop\\STARTUP\\StyleTribe\\Comms\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

options = webdriver.ChromeOptions()
options.binary_location = canary_path

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# Open WhatsApp Web and wait for user to scan the QR code.
driver.get("https://web.whatsapp.com/")
print("Please scan the QR code in the opened browser window. Then press Enter here to continue...")
input()  # Wait for manual confirmation once QR scanning is done

# ----------------------------
# Job Queue and Worker Thread
# ----------------------------
class Job:
    def __init__(self, phone_number, message_body):
        self.phone_number = phone_number
        self.message_body = message_body
        self.result = None
        self.event = threading.Event()

job_queue = queue.Queue()

def worker():
    while True:
        job = job_queue.get()
        try:
            encoded_message = urllib.parse.quote(job.message_body, safe='', encoding='utf-8')
            chat_url = f"https://web.whatsapp.com/send?phone={job.phone_number}&text={encoded_message}"
            
            driver.get(chat_url)
            
            wait = WebDriverWait(driver, 20)
            send_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@aria-label="Send"]')
            ))
            
            send_button.click()
            job.result = {"status": "success", "message": "WhatsApp message sent successfully"}
        except Exception as e:
            job.result = {"status": "failed", "error": str(e)}
        finally:
            job.event.set()
            job_queue.task_done()
            # 5-second wait after processing the job
            time.sleep(5)

threading.Thread(target=worker, daemon=True).start()

# ----------------------------
# Flask API Endpoint
# ----------------------------
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
    data = request.json
    phone_number = data.get('phone_number')
    message_body = data.get('message_body')
    
    if not phone_number or not message_body:
        return jsonify({"error": "Missing phone_number or message_body"}), 400

    job = Job(phone_number, message_body)
    job_queue.put(job)
    job.event.wait()
    
    return jsonify(job.result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
