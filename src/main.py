from loguru import logger
from flask import Flask
from flask import Response, jsonify
from flask_cors import CORS
import base64
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import multiprocessing
import json
import base64
import os
import random
import string
import time


app = Flask(__name__)
CORS(app)


def gather_data(b64url, filename):    
    url = base64.b64decode(b64url).decode('utf-8')
        
    # Getting the URL in the browser
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    service = Service(executable_path="/app/geckodriver")

    driver = webdriver.Firefox(options=options, service=service)
    driver.set_window_size(1200, 900)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(url)
    
    page_title = driver.title
    
    # Getting the actual screenshot
    screenshot = driver.get_screenshot_as_png()
    screenshot_buffer = BytesIO(screenshot)
    
    # Resizing the image
    image = Image.open(screenshot_buffer)
    resized_image = image.resize((540, 300), Image.LANCZOS)
    
    # Resized buffer
    resized_buffer = BytesIO()
    resized_image.save(resized_buffer, format="PNG")
    
    # Convert to base64
    resized_bytes = resized_buffer.getvalue()
    base64_string = base64.b64encode(resized_bytes).decode("utf-8")
    
    # Quitting the driver
    driver.quit()
    
    response = {
        "b64buffer": base64_string,
        "page_title": page_title
    }
    
    # Save to temporary directory
    with open(f"./tmp/{filename}", "w") as output_file:
        output_file.write(base64.b64encode(json.dumps(response).encode()).decode('utf-8'))


def load_data(b64url, filename, remove_after_read=False):
    with open(f"./tmp/{filename}", "r") as input_file:
        content = json.loads(base64.b64decode(input_file.read()).decode('utf-8'))
    
    if remove_after_read:
        os.remove(f"./tmp/{filename}")
        
    return content


@app.route("/url-preview/<b64url>")
def hello_world(b64url):
    try:
        # Get current time with microsecond precision
        random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=48))

        # Gather data
        p = multiprocessing.Process(target=gather_data, args=(b64url, random_filename))
        p.start()
        
        # Waiting for process to finish
        p.join()
        
        response = load_data(b64url, random_filename, remove_after_read=True)
        
        return jsonify(response)
    except Exception as e:
        return Response(
            "Error during URL request",
            status=500
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=42069)
