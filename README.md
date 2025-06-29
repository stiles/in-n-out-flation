# In-n-out price tracker

This project uses OpenAI's GPT-4o model to analyze screenshots of In-N-Out drive-thru menus from Google Street View. It extracts menu item prices, calorie counts and the date and location of the photo, compiling the data into a single JSON file. This allows for tracking menu price inflation over time.

## Key findings

> The graph tells a story of a long period where the Double-Double was a famously good deal, followed by a recent and sharp correction where its price is now rising faster than the average cost of eating out.

![In-N-Out Double-Double Price vs. Inflation](plots/doubledouble_price_vs_inflation.png)

## Data source

In-N-Out does not publicly release historical menu pricing. To work around this limitation, this project uses screenshots from Google Street View's historical imagery. This provides a snapshot of menu prices at different locations and times, creating a unique dataset for tracking price changes.

## How it works

The script in `scripts/extract_menu_data.py` processes each image in the `images/` folder. For each image, it sends a request to the GPT-4o vision model with a prompt asking for specific information:

-   Date (month and year) from the Google Street View UI.
-   GPS coordinates (latitude and longitude) if visible in the URL.
-   Prices and calorie counts for key menu items.

The model returns a JSON object with the extracted data which is then flattened and collected. The final output is saved to `data/menu_inflation.json`.

## Setup

1.  **Install dependencies**

    Make sure Python is installed. Then, install the required packages.

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables**

    The script requires an OpenAI API key and a Bureau of Labor Statistics (BLS) API key. Create a `.env` file in the root of the project and add the keys. You can get a free BLS key from their [website](https://data.bls.gov/registrationEngine/).

    ```
    OPENAI_API_KEY="your-openai-api-key-here"
    BLS_API_KEY="your-bls-api-key-here"
    ```

## Usage

### 1. Extract data from images

First, place screenshots of In-N-Out menus from Google Street View into the `images/` directory.

Then, execute the extraction script from the project root.

```bash
python scripts/extract_menu_data.py
```

The script will process each image and save the results to `data/menu_inflation.json`.

### 2. Analyze price changes

Once you have generated the data file, you can run the analysis script. This script fetches the latest inflation data from the BLS, compares item prices over time, and generates charts in the `plots/` directory.

```bash
python scripts/analyze_price_changes.py
```

The script will output a clear takeaway, explaining how the item's price has changed relative to inflation. You can configure the item and dates directly in the script.

## Project structure

```
.
├── data/
│   └── menu_inflation.json       # Output file with extracted data
├── images/
│   └── ...                       # Input images of menus
├── plots/
│   ├── doubledouble_price_vs_inflation.png # Output chart
│   └── ...                       # Other generated plots
├── scripts/
│   ├── extract_menu_data.py      # Main data extraction script
│   └── analyze_price_changes.py  # Price analysis script
├── .env                          # Environment variables (needs to be created)
└── requirements.txt              # Python package dependencies
``` 