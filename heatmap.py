from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


DATA_FILE = Path(__file__).with_name("miso_demand_features.csv")
OUTPUT_FILE = Path(__file__).with_name("miso_demand_heatmap.png")
WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def main():
    df = pd.read_csv(DATA_FILE)
    required_columns = {"value", "hour", "day_name"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"{DATA_FILE.name} is missing required columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    demand_by_day_and_hour = (
        df.pivot_table(
            index="day_name",
            columns="hour",
            values="value",
            aggfunc="mean",
        )
        .reindex(index=WEEKDAYS, columns=range(24))
    )

    plt.figure(figsize=(14, 6))
    sns.heatmap(
        demand_by_day_and_hour,
        cmap="YlOrRd",
        linewidths=0.25,
        cbar_kws={"label": "Average demand (MW)"},
    )
    plt.title("Average MISO Electricity Demand by Day and Hour")
    plt.xlabel("Hour of day (Central Time)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight")
    print(f"Saved heatmap to {OUTPUT_FILE}")
    plt.show()


if __name__ == "__main__":
    main()
