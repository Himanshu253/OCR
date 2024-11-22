from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import pytesseract  # Use pytesseract for OCR
import pandas as pd
import json

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def process_image(image_path):
    """
    Processes the image to extract data and generate JSON output.

    Args:
        image_path (str): Path to the uploaded image file.

    Returns:
        dict: JSON data containing extracted details.
    """

    try:

        img = cv2.imread(image_path)

        # Pre-process the image (adjust parameters as needed)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Extract text using pytesseract (adjust configuration parameters if needed)
        text = pytesseract.image_to_string(thresh, config='--psm 6')  # Treat as single block

        # Parse the extracted text to create a list of rows
        rows = []
        for line in text.splitlines():
            # Split the line based on delimiters or use regular expressions for more complex parsing
            row_data = line.strip().split(' ')  # Replace delimiter if necessary
            rows.append(row_data)

        # Create JSON output with desired structure
        json_data = {
            "data": [
                ["Type", "Product", "Started Date", "Completed Date", "Description", "Amount", "Fee", "Currency", "State", "Balance"],  # Header row
                *rows  # List of data rows
            ]
        }

        return json_data

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        result_data = process_image(file_path)

        if result_data:  # Check for successful processing
            return jsonify(result_data)
        else:
            return jsonify({'error': 'Error processing image'}), 500  # Indicate an error

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)