import os
import time
import threading
from openai import OpenAI
from pprint import pprint
from dotenv import load_dotenv
import base64

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_user_input(prompt: str):
    return input(prompt)

def status_printer(stop_event): 
    dots = 1 
    while not stop_event.is_set(): 
        print("\rGenerating" + "." * dots + " " * (5 - dots), end="", flush=True) 
        dots = dots + 1 if dots < 5 else 1 
        time.sleep(2)

user_input=get_user_input("Enter your prompt: ")



def generate_filename(prompt: str): 
    stop_event = threading.Event() 
    t = threading.Thread(target=status_printer, args=(stop_event,)) 
    t.start() 
    
    try:
        response = client.responses.create(
        model="gpt-5-nano",
        input=( "Create a single short PNG filename based on this topic: " + prompt + 
            ". The filename must:\n" 
            "- be one word or hyphenated\n" 
            "- contain no spaces\n" 
            "- contain only letters, numbers, or hyphens\n" 
            "- end with .png\n" 
            "- be at most 18 characters total (including .png)\n" 
            "Output ONLY the filename. No explanations. No alternatives.")
        )
    finally: 
        stop_event.set() 
        t.join() 
    return response   
  


def generate_image(prompt: str): 
    stop_event = threading.Event() 
    t = threading.Thread(target=status_printer, args=(stop_event,)) 
    t.start() 
    
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input="Create image of: " + prompt,
            tools=[{"type": "image_generation"}],
        )
    finally: 
        stop_event.set() 
        t.join() 
    return response   



response = generate_filename(user_input)
filename = response.output_text
print("Filename: ", filename)
response = generate_image(user_input)       

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))



