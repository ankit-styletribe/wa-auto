import time
import urllib.parse
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Paths (update these as needed)
canary_path = "C:\\Users\\ankit\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe"
chromedriver_path = "C:\\Users\\ankit\\Desktop\\STARTUP\\StyleTribe\\Comms\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# Set up Chrome options
options = webdriver.ChromeOptions()
options.binary_location = canary_path

# Initialize WebDriver with explicit ChromeDriver path
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# Open WhatsApp Web and let the user log in by scanning the QR code.
driver.get("https://web.whatsapp.com/")
print("Please scan the QR code in the opened browser window. Then press Enter here to continue...")
input()  # Wait for manual confirmation once QR scanning is done

# --- Flask API Endpoint ---
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
    data = request.json
    phone_number = data.get('phone_number')
    message_body = data.get('message_body')
    
    if not phone_number or not message_body:
        return jsonify({"error": "Missing phone_number or message_body"}), 400

    # Encode the message ensuring UTF-8 encoding for emojis and other special characters
    encoded_message = urllib.parse.quote(message_body, safe='', encoding='utf-8')
    chat_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"

    try:
        # Navigate to the conversation page
        driver.get(chat_url)

        # Wait until the send button becomes clickable (adjust the timeout as needed)
        wait = WebDriverWait(driver, 20)
        send_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@aria-label="Send"]')
        ))

        # Simulate a click on the send button
        send_button.click()

        return jsonify({"status": "success", "message": "WhatsApp message sent successfully"}), 200

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)