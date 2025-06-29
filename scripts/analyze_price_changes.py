import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import date
from dotenv import load_dotenv
from matplotlib.ticker import FuncFormatter

# Load environment variables from .env file
load_dotenv()

# 🔧 Config
DATA_FILE = "data/menu_inflation.json"
PLOT_DIR = "plots"
# U.S. national average for "Food away from home"
CPI_SERIES_ID = "CUUR0000SEFV"

# Items to analyze
ITEMS_TO_ANALYZE = {
    "Double-Double": "doubledouble_price",
    "Cheeseburger": "cheeseburger_price",
    "Hamburger": "hamburger_price",
    "French Fries": "frenchfries_price",
}

def get_cpi_data(start_year, end_year):
    """
    Fetches CPI data for a given series ID and year range directly from the BLS API.
    """
    api_key = os.getenv("BLS_API_KEY")
    if not api_key:
        print("BLS_API_KEY not found in .env file. Please get a key from https://data.bls.gov/registrationEngine/")
        return None

    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": [CPI_SERIES_ID],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": api_key
    })

    try:
        response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()

        if result['status'] != 'REQUEST_SUCCEEDED':
            print(f"BLS API request failed: {result.get('message', ['Unknown error.'])[0]}")
            return None

        # Process the data into a DataFrame
        series_data = result['Results']['series'][0]['data']
        df = pd.DataFrame(series_data)
        df['date'] = pd.to_datetime(df['year'] + '-' + df['periodName'] + '-01')
        df.set_index('date', inplace=True)
        df['value'] = pd.to_numeric(df['value'])
        return df[['value']].resample('MS').mean()

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from BLS API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Could not parse BLS API response: {e}")
        return None

def clean_data(data):
    """Cleans and prepares the menu price data for analysis."""
    df = pd.DataFrame(data)
    price_cols = list(ITEMS_TO_ANALYZE.values())
    df = df.dropna(subset=["year", "month"] + price_cols, how='any')

    month_to_num = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    df["month"] = df["month"].map(month_to_num)
    df = df.dropna(subset=["month"])
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    
    for col in price_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=price_cols)
    df = df.sort_values("date")
    
    # Average prices for the same month
    df = df.groupby('date')[price_cols].mean().reset_index()
    
    return df

def plot_price_trends(df, cpi_df):
    """Plots actual vs. inflation-adjusted Double-Double price."""
    # --- Font and Style Setup ---
    try:
        plt.rcParams['font.family'] = 'Roboto'
    except RuntimeError:
        print("Roboto font not found, using default.")
        
    plt.style.use("seaborn-v0_8-whitegrid")

    # --- Data Preparation ---
    item_col = ITEMS_TO_ANALYZE["Double-Double"]
    df_item = df[["date", item_col]].copy().set_index('date')
    
    merged_df = df_item.join(cpi_df, how='left')
    merged_df['value'] = merged_df['value'].ffill().bfill()

    end_cpi = merged_df['value'].iloc[-1]
    merged_df['price_today_equivalent'] = merged_df.apply(
        lambda row: row[item_col] * end_cpi / row['value'], axis=1
    )

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(merged_df.index, merged_df[item_col], "o-", label="Actual Price", color="red")
    ax.plot(merged_df.index, merged_df['price_today_equivalent'], "x--", label=f"Price in {merged_df.index[-1].year} Dollars", color="black")

    # --- Formatting and Labels ---
    ax.set_title("In-N-Out Double-Double Price vs. Inflation", fontsize=16, pad=20, fontweight='bold')
    
    # Custom currency formatter for the y-axis
    def currency_formatter(x, pos):
        if x == int(x):
            return f'${int(x)}'
        return f'${x:.2f}'
    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

    ax.legend()
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)

    plt.xticks(rotation=0) # Set x-axis labels to be horizontal
    plt.tight_layout()
    
    save_path = os.path.join(PLOT_DIR, "doubledouble_price_vs_inflation.png")
    plt.savefig(save_path, dpi=300)
    print(f"\n📈 Trend plot saved to '{save_path}'")

def plot_item_price_summary(df):
    """Generates a bar chart comparing the start and end prices."""
    price_data = []
    start_date = df["date"].iloc[0]
    end_date = df["date"].iloc[-1]

    for name, col in ITEMS_TO_ANALYZE.items():
        start_price = df[df["date"] == start_date][col].mean()
        end_price = df[df["date"] == end_date][col].mean()
        if pd.notna(start_price) and pd.notna(end_price):
            price_data.append({"item": name, "price": start_price, "date_str": start_date.strftime("%b %Y")})
            price_data.append({"item": name, "price": end_price, "date_str": end_date.strftime("%b %Y")})

    df_plot = pd.DataFrame(price_data)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12, 7))

    sns.barplot(data=df_plot, x="item", y="price", hue="date_str", ax=ax, palette="viridis")
    
    ax.set_title("Price Increase of In-N-Out Menu Items", fontsize=16, pad=20)
    ax.set_ylabel("Price ($)")
    ax.set_xlabel("")
    ax.legend(title="Date")
    plt.tight_layout()

    save_path = os.path.join(PLOT_DIR, "item_price_increases.png")
    plt.savefig(save_path, dpi=300)
    print(f"📊 Bar chart saved to '{save_path}'")

def main():
    """Analyzes and visualizes In-N-Out menu price changes."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at '{DATA_FILE}'.")
        print("Please run `extract_menu_data.py` first.")
        return

    df = clean_data(data)
    if df.empty:
        print("No valid data to analyze after cleaning.")
        return

    start_year = df['date'].dt.year.min()
    end_year = df['date'].dt.year.max()
    cpi_df = get_cpi_data(start_year, end_year)

    if cpi_df is None:
        print("Could not fetch CPI data. Aborting analysis.")
        return

    print(f"Successfully fetched CPI data for series '{CPI_SERIES_ID}'")

    plot_price_trends(df, cpi_df)
    plot_item_price_summary(df)

if __name__ == "__main__":
    main() 