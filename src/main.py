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

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
service = Service(executable_path="/app/geckodriver")

app = Flask(__name__)
CORS(app)


@app.route("/url-preview/<b64url>")
def hello_world(b64url):
    try:
        url = base64.b64decode(b64url).decode('utf-8')
        
        # Getting the URL in the browser
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
        
        return jsonify(response)
    except Exception as e:
        # raise e
        return Response(
            "Error during URL request",
            status=500
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=42069)
