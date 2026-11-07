
import pandas as pd
import numpy as np
from pathlib import Path

# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
CALIBRATION_DIR = PROJECT_DIR / "data" / "calibration"

WATER_FILE = CALIBRATION_DIR / "water_sensor_calibration.xlsx"
LOADCELL_FILE = CALIBRATION_DIR / "loadcell_calibration.xlsx"


# ==================================================
# 1. GENERAL CALIBRATION FUNCTION
# ==================================================

def calculate_calibration(csv_path, adc_column="adc"):

    path = Path(csv_path)

    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    if adc_column not in df.columns:
        raise ValueError(
            f"Column '{adc_column}' not found."
        )

    readings = pd.to_numeric(
        df[adc_column], errors="coerce"
    ).dropna()

    if readings.empty:
        raise ValueError("No valid readings found.")

    return readings.mean(), readings.std()


# ==================================================
# 2. WATER SENSOR PROCESSING
# ==================================================

def process_water_sensor():

    print("\n" + "=" * 55)
    print("WATER SENSOR CALIBRATION")
    print("=" * 55)

    if not WATER_FILE.exists():
        raise FileNotFoundError(WATER_FILE)

    # Read only Raw_Data
    df = pd.read_excel(
        WATER_FILE,
        sheet_name="Raw_Data"
    )

    # Identify columns
    level_col = next(
        (c for c in df.columns
         if "level" in str(c).lower()),
        None
    )

    adc_col = next(
        (c for c in df.columns
         if "adc" in str(c).lower()),
        None
    )

    if level_col is None or adc_col is None:
        raise ValueError(
            f"Water columns not identified: {df.columns.tolist()}"
        )

    df[level_col] = pd.to_numeric(
        df[level_col], errors="coerce"
    )

    df[adc_col] = pd.to_numeric(
        df[adc_col], errors="coerce"
    )

    df = df.dropna(subset=[level_col, adc_col])

    summary = (
        df.groupby(level_col)[adc_col]
        .agg(
            sample_count="count",
            mean_adc="mean",
            std_adc="std",
            min_adc="min",
            max_adc="max"
        )
        .reset_index()
    )

    print("\nWater Sensor Summary:")
    print(summary.to_string(index=False))

    # Preserve existing sheets
    with pd.ExcelWriter(
        WATER_FILE,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Day25_Water_Summary",
            index=False
        )

    print("\nWater sensor summary saved.")


# ==================================================
# 3. LOAD CELL PROCESSING
# ==================================================

def process_loadcell():

    print("\n" + "=" * 55)
    print("LOAD CELL CALIBRATION")
    print("=" * 55)

    if not LOADCELL_FILE.exists():
        raise FileNotFoundError(LOADCELL_FILE)

    df = pd.read_excel(
        LOADCELL_FILE,
        sheet_name="Sheet1"
    )

    # Required columns
    required = [
        "Attempt",
        "Calibration Factor",
        "Known Weight (g)",
        "Calibration Check (g)",
        "Trial",
        "Measured Weight (g)",
        "Absolute Error (g)",
        "Error (%)"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"Missing column: {col}"
            )

    numeric_cols = [
        "Calibration Factor",
        "Known Weight (g)",
        "Calibration Check (g)",
        "Trial",
        "Measured Weight (g)",
        "Absolute Error (g)",
        "Error (%)"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(
        subset=["Attempt", "Measured Weight (g)"]
    )

    # Summary by calibration attempt
    summary = (
        df.groupby("Attempt")
        .agg(
            calibration_factor=("Calibration Factor", "first"),
            known_weight_g=("Known Weight (g)", "first"),
            calibration_check_g=("Calibration Check (g)", "first"),
            sample_count=("Measured Weight (g)", "count"),
            mean_measured_weight_g=("Measured Weight (g)", "mean"),
            std_measured_weight_g=("Measured Weight (g)", "std"),
            mean_absolute_error_g=("Absolute Error (g)", "mean"),
            mean_error_percent=("Error (%)", "mean"),
            min_measured_weight_g=("Measured Weight (g)", "min"),
            max_measured_weight_g=("Measured Weight (g)", "max")
        )
        .reset_index()
    )

    print("\nLoad Cell Summary:")
    print(summary.to_string(index=False))

    # Save new summary sheet
    with pd.ExcelWriter(
        LOADCELL_FILE,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Day25_LoadCell_Summary",
            index=False
        )

    print("\nLoad cell summary saved.")

    print("\nCalibration Assessment:")

    for _, row in summary.iterrows():

        print(
            f"Attempt {row['Attempt']}: "
            f"Mean = {row['mean_measured_weight_g']:.2f} g, "
            f"Mean Error = {row['mean_error_percent']:.2f}%"
        )


# ==================================================
# 4. MAIN
# ==================================================

if __name__ == "__main__":

    print("\nDAY 25: CALIBRATION CALCULATION")
    print("-" * 55)

    process_water_sensor()

    process_loadcell()

    print("\n" + "=" * 55)
    print("DAY 25 PROCESSING FINISHED")
    print("=" * 55)
