import os
import openai
import base64
import json
from tqdm import tqdm
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 🔧 Config
# Initialize the OpenAI client. It will automatically pick up the OPENAI_API_KEY.
try:
    client = openai.OpenAI()
    # Test the key by making a simple API call
    client.models.list()
except openai.AuthenticationError:
    raise ValueError(
        "OPENAI_API_KEY is invalid or not set. Please check your .env file."
    )
except Exception as e:
    raise e

image_folder = "images"
output_json = "data/menu_inflation.json"

def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')

def build_prompt():
    return """
You are looking at a drive-thru menu at an In-N-Out location, taken from a Google Street View screenshot.

Please extract the following information:

1.  **Location**: The latitude and longitude, if visible in the browser's URL bar. If not visible, return `null` for `lat` and `lon`.
2.  **Date**: The month and year shown in the top left of the Google Street View interface.
3.  **Menu Items**: For each of the following items, extract the price and calories.
    - Double-Double
    - Cheeseburger
    - Hamburger
    - French Fries
    - Shakes

**Formatting Rules**:
- Return a single valid JSON object.
- For each menu item, **always return an object**.
- If a `price` or `calories` value is not visible or cannot be determined for an item, return `null` for that specific field. Do not omit the item itself.

Example of the expected JSON structure:
{
  "lat": 33.9535714,
  "lon": -118.3967684,
  "month": "November",
  "year": 2020,
  "items": {
    "doubledouble": {"price": 4.45, "calories": 670},
    "cheeseburger": {"price": 3.10, "calories": 480},
    "hamburger": {"price": 2.75, "calories": null},
    "frenchfries": {"price": 2.05, "calories": 370},
    "shakes": {"price": null, "calories": null}
  }
}
"""

def query_gpt_with_image(img_path):
    img_b64 = encode_image(img_path)
    prompt = build_prompt()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                ],
            }
        ],
        max_tokens=1000,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content

def flatten_result(content, filename):
    try:
        result = json.loads(content)
        flat = {
            "image": filename,
            "lat": result.get("lat"),
            "lon": result.get("lon"),
            "month": result.get("month"),
            "year": result.get("year"),
        }
        items = result.get("items", {})
        for item, info in items.items():
            safe_item = item.replace(" ", "_")
            flat[f"{safe_item}_price"] = info.get("price")
            flat[f"{safe_item}_calories"] = info.get("calories")
        return flat
    except Exception as e:
        return {"image": filename, "error": str(e), "raw_response": content}

def main():
    results = []
    image_files = sorted(
        [
            f
            for f in os.listdir(image_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )

    if not image_files:
        print(f"No images found in '{image_folder}'. Please check the path.")
        return

    for filename in tqdm(image_files, desc="Processing images"):
        path = os.path.join(image_folder, filename)
        try:
            content = query_gpt_with_image(path)
            result = flatten_result(content, filename)
            results.append(result)
        except Exception as e:
            print(f"Could not process {filename}. Error: {e}")
            results.append({"image": filename, "error": str(e)})

    # Sort results by year and month, descending.
    month_to_num = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    results.sort(
        key=lambda r: (r.get("year", 0), month_to_num.get(r.get("month"), 0)),
        reverse=True,
    )

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Done! Saved to {output_json}")

if __name__ == "__main__":
    main()
