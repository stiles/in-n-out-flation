# 🧾 In-N-Out Menu Inflation Project

**Goal:**  
Analyze price and calorie inflation (including shrinkflation) of In-N-Out's drive-thru menu over time using historical Google Street View imagery.

---

## 📍 Location Target

We focus on a specific In-N-Out location in Los Angeles:

- **Latitude**: `33.9535714`  
- **Longitude**: `-118.3967684`  
- **Example URL**:  
  `https://www.google.com/maps/@33.9535714,-118.3967684,3a,15y,39.91h,84.26t/data=!3m7!1e1!3m5!1s1cI7j1Bkqc_hM-wUJF4v9w`

---

## 🧠 Idea

Since In-N-Out doesn't publish prices online, we'll:
- Collect screenshots of the drive-thru menu from Google Street View across years
- Use an OpenAI Vision model to extract structured data from each image
- Compare price and calorie changes over time for core menu items

---

## 📂 Image Directory Structure

You've collected 24 images saved here:

```
in-n-out/
└── images/
    ├── Screenshot 2025-06-28 at 11.33.17 AM.png
    ├── Screenshot 2025-06-28 at 11.33.29 AM.png
    └── ...
```

---

## 🔍 Data Points to Extract per Image

From each image, we will extract:
- `lat`, `lon` from browser URL (if visible)
- `month`, `year` from Street View UI
- For each menu item:
  - **Double-Double**
  - **Cheeseburger**
  - **Hamburger**
  - **French Fries**
  - **Shakes**  
  → Extract both `price` and `calories`

---

## 🛠️ Script Overview

A Python script will:
1. Loop through all images in `in-n-out/images/`
2. Send each image to the OpenAI Vision API
3. Prompt the model to return structured JSON
4. Flatten the result into a row for a CSV
5. Save everything to `in-n-out/menu_inflation.csv`

### Technologies Used
- `openai` for API calls
- `base64`, `os`, `json` for handling image inputs
- `tqdm`, `pandas` for looping and output

---

## ✅ Output: `menu_inflation.csv`

A wide-format CSV with columns like:

| image        | month    | year | Double-Double_price | Double-Double_calories | Cheeseburger_price | ... |
|--------------|----------|------|----------------------|-------------------------|---------------------|-----|
| Screenshot…  | Nov      | 2020 | 4.45                 | 670                     | 3.10                |     |

---

## 🧱 Next Steps

- [ ] Run the script on all 24 screenshots
- [ ] Spot check the extracted data for accuracy
- [ ] Join with CPI data to calculate real inflation
- [ ] Visualize price vs calorie trends over time

---

## 🌐 API Keys Used

This project uses an `OPENAI_API_KEY` for the Vision API. The script is configured to load this key from a `.env` file in the project root.

1.  Create a file named `.env`.
2.  Add the key to it: `OPENAI_API_KEY="YOUR_KEY_HERE"`

The `.gitignore` file is set up to prevent this file from being committed.
