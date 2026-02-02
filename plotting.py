# Mapping and geospatial visualization
import folium

# Data manipulation
import pandas as pd
import json

# For injecting custom HTML/CSS into folium maps
from folium import Element

# Plotting libraries
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import seaborn as sns

# Numerical operations
import numpy as np

# Statistical testing and confidence intervals
from scipy.stats import ttest_ind
import scipy.stats as stats


# -------------------------------------------------
# 1. Display an interactive choropleth map by region
# -------------------------------------------------
def displayMap(df_map):
    # Aggregate total profit and store count per region
    df_region = (
        df_map
        .groupby("region", as_index=False)
        .agg(
            total_profit=("total_profit", "sum"),
            store_count=("store_count", "sum")
        )
    )

    # Create a lookup table indexed by region name
    region_lookup = df_region.set_index("region")

    # -------------------------------------------------
    # 2. Load UK regions GeoJSON file
    # -------------------------------------------------
    with open("uk_regions.geojson") as f:
        uk_geo = json.load(f)

    # -------------------------------------------------
    # 3. Inject aggregated data into GeoJSON properties
    #    (used later for hover tooltips)
    # -------------------------------------------------
    for feature in uk_geo["features"]:
        region = feature["properties"]["rgn19nm"]

        # If region exists in dataset, attach values
        if region in region_lookup.index:
            row = region_lookup.loc[region]
            feature["properties"]["store_count"] = int(row.store_count)
            feature["properties"]["total_profit"] = f"£{row.total_profit/1000000:,.2f} Millions"
        else:
            # Default values for missing regions
            feature["properties"]["store_count"] = 0
            feature["properties"]["total_profit"] = "£0"

    # -------------------------------------------------
    # 4. Create base map (without labels)
    # -------------------------------------------------
    m = folium.Map(
        location=[54.5, -3],          # Centered on the UK
        zoom_start=6,
        tiles="CartoDB Positron No Labels",
    )

    # -------------------------------------------------
    # 5. Add choropleth layer based on total profit
    # -------------------------------------------------
    folium.Choropleth(
        geo_data=uk_geo,
        data=df_region,
        columns=["region", "total_profit"],
        key_on="feature.properties.rgn19nm",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.3,
        legend_name="Total Profit (£)"
    ).add_to(m)

    # -------------------------------------------------
    # 6. Styling functions for hover interaction
    # -------------------------------------------------
    def style_function(feature):
        # Default region styling (invisible fill)
        return {
            "fillColor": "transparent",
            "color": "black",
            "weight": 0.4,
            "fillOpacity": 0
        }

    def highlight_function(feature):
        # Styling when hovering over a region
        return {
            "weight": 2,
            "color": "black",
            "fillOpacity": 0.15
        }

    # -------------------------------------------------
    # 7. GeoJSON layer for hover tooltips only
    #    (no click-based interaction)
    # -------------------------------------------------
    folium.GeoJson(
        uk_geo,
        style_function=style_function,
        highlight_function=highlight_function,
        zoom_on_click=False,
        tooltip=folium.GeoJsonTooltip(
            fields=["rgn19nm", "store_count", "total_profit"],
            aliases=["Region:", "Stores:", "Total Profit:"],
            sticky=True
        )
    ).add_to(m)

    # -------------------------------------------------
    # 8. Remove black focus outline on click (CSS fix)
    # -------------------------------------------------
    m.get_root().html.add_child(
        Element("""
        <style>
            .leaflet-interactive {
                outline: none !important;
            }
        </style>
        """)
    )

    # -------------------------------------------------
    # 9. Return final interactive map
    # -------------------------------------------------
    return m


# -------------------------------------------------
# Plot total profit by sales month
# -------------------------------------------------
def salesMonth(df):
    # Define correct chronological month order
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Convert sales_month column to ordered categorical
    df["sales_month"] = pd.Categorical(df["sales_month"],
                                       categories=month_order,
                                       ordered=True)

    # Sort DataFrame based on month order
    df.sort_values("sales_month", inplace=True)

    # Attempt to clean and convert profit column if stored as string
    try:
        df['total_profit'] = df['total_profit'].str.replace(',', '')
        df['total_profit'] = pd.to_numeric(df['total_profit'])
    except:
        pass

    # Create bar chart
    plt.figure(figsize=(8, 5))

    # Display total yearly profit as annotation
    plt.text(
        0.5, 0.95,
        f"Total Yearly Profit: {sum(df['total_profit'])/ 1_000_000:,.2f} M",
        ha="center",
        va="center",
        transform=plt.gca().transAxes
    )

    # Plot monthly profit
    plt.bar(df["sales_month"], df["total_profit"])
    plt.xticks(rotation=45)
    plt.title("Total Profit by Sales Month")
    plt.xlabel("Sales Month")

    # Format y-axis values in millions
    plt.gca().yaxis.set_major_formatter(
        mtick.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M')
    )

    plt.ylabel("Total Profit")
    plt.tight_layout()
    plt.show()


# -------------------------------------------------
# Display donut chart for contribution analysis
# -------------------------------------------------
def displayDonut(ax, purchase_contributions, vendors, total_contribution, title, colors=None, text11=None):

    # Draw pie chart
    ax.pie(
        purchase_contributions,
        labels=vendors,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.85,
        colors=colors
    )

    # Create donut hole
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)

    # Add center text showing total contribution
    ax.text(
        0, 0,
        f"{text11}:\n{total_contribution:.2f}%",
        fontsize=12,
        fontweight='bold',
        ha='center',
        va='center'
    )

    # Set chart title
    ax.set_title(title)


# -------------------------------------------------
# Compute confidence interval for a dataset
# -------------------------------------------------
def confidence_interval(data, confidence=0.95):
    # Mean of data
    mean_val = np.mean(data)

    # Standard error of the mean
    std_err = np.std(data, ddof=1) / np.sqrt(len(data))

    # Critical t-value for given confidence level
    t_critical = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)

    # Margin of error
    margin_of_error = t_critical * std_err

    # Return mean and confidence interval bounds
    return mean_val, mean_val - margin_of_error, mean_val + margin_of_error


# -------------------------------------------------
# Plot confidence interval comparison between vendors
# -------------------------------------------------
def confidence_interval_plot(top_vendors, low_vendors):
    # Compute confidence intervals for both groups
    top_mean, top_lower, top_upper = confidence_interval(top_vendors)
    low_mean, low_lower, low_upper = confidence_interval(low_vendors)

    # Print interval statistics
    print(f"Top Vendors 95% CI: ({top_lower:.2f}, {top_upper:.2f}), Mean: {top_mean:.2f}")
    print(f"Low Vendors 95% CI: ({low_lower:.2f}, {low_upper:.2f}), Mean: {low_mean:.2f}")

    plt.figure(figsize=(12, 6))

    # KDE plot for top vendors
    sns.kdeplot(top_vendors, color="blue", alpha=0.5, label="Top Vendors")

    # Mark confidence interval and mean
    plt.axvline(top_lower, color="blue", linestyle="--", label=f"Top Lower: {top_lower:.2f}")
    plt.axvline(top_upper, color="blue", linestyle="--", label=f"Top Upper: {top_upper:.2f}")
    plt.axvline(top_mean, color="blue", linestyle="-", label=f"Top Mean: {top_mean:.2f}")

    # KDE plot for low vendors
    sns.kdeplot(low_vendors, color="red", alpha=0.5, label="Low Vendors")

    # Mark confidence interval and mean
    plt.axvline(low_lower, color="red", linestyle="--", label=f"Low Lower: {low_lower:.2f}")
    plt.axvline(low_upper, color="red", linestyle="--", label=f"Low Upper: {low_upper:.2f}")
    plt.axvline(low_mean, color="red", linestyle="-", label=f"Low Mean: {low_mean:.2f}")

    # Final plot formatting
    plt.title("Confidence Interval Comparison: Top vs. Low Vendors (Profit Margin)")
    plt.xlabel("Profit Margin (%)")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(False)
    plt.show()


# -------------------------------------------------
# Format numeric values into readable dollar strings
# -------------------------------------------------
def format_dollars(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(value)
