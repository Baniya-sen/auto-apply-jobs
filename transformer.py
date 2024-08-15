import time

import pyautogui
import pytesseract
from PIL import Image
from transformers import pipeline

from get_div_size import open_a, apply, next_a, take_apply_form_screenshot


open_a()
apply()

width, height = take_apply_form_screenshot
region = (570, 180, width, height)
screenshot = pyautogui.screenshot(region=region)
screenshot.save("question_box.png")

next_a()

width, height = take_apply_form_screenshot
region = (570, 180, width, height)
screenshot = pyautogui.screenshot(region=region)
screenshot.save("question_box1.png")

# # Step 3: Extract text from the screenshot
# text = pytesseract.image_to_string(screenshot)
#
# # Step 4: Process the extracted text (basic example)
# # Here you could apply further filtering to clean up the text
#
# # Step 5: Use a question-answering model (example)
# # Load a pre-trained question answering model
# qa_model = pipeline("question-answering")
#
# # Example question (replace with the actual extracted text)
# questions = ["What is the capital of France?"]
#
# # Assume 'text' contains the relevant passage from which to answer
# for question in questions:
#     result = qa_model(question=question, context=text)
#     print(f"Answer: {result['answer']}")
