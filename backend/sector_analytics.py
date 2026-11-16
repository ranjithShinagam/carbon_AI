# ============================================================
# Carbon AI - Sector Analytics
# ============================================================
# Generates real sector-wise and industry-wise analytics.
#
# Works with:
#   - Original Carbon AI dataset
#   - Adapted user-uploaded dataset
#   - Dataset after batch XGBoost prediction
#
# No mock/random values are used.
# ============================================================

from typing import Dict, Any, List

import numpy as np
import pandas as pd


# ============================================================
# COLUMN NAMES
# ============================================================

SECTOR_COLUMN = "Sector"

INDUSTRY_COLUMN = "Industry_Sectors"

ACTUAL_TARGET_COLUMN = "Carbon_Emission_tCO2e_TARGET"

PREDICTION_COLUMN = "Predicted_Carbon_Emission_tCO2e"

TOTAL_ENERGY_COLUMN = "Total_Energy_Consumption_kWh"

RENEWABLE_ENERGY_COLUMN = "Renewable_Energy_Consumption_kWh"

NONRENEWABLE_ENERGY_COLUMN = "NonRenewable_Energy_Consumption_kWh"

PRODUCTION_COLUMN = "Production_Output_Units"

TRANSPORT_COLUMN = "Supply_Chain_Transport_km"

RAW_MATERIAL_COLUMN = "Raw_Material_Usage_kg"

EMPLOYMENT_COLUMN = "Employment_Count"


# ============================================================
# HELPERS
# ============================================================

def safe_mean(series: pd.Series) -> float:
    """
    Safely calculate the mean of a pandas Series.
    Invalid/non-numeric values are ignored.
    """

    if series is None:
        return 0.0

    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )

    if numeric.dropna().empty:
        return 0.0

    return float(numeric.mean())


def safe_sum(series: pd.Series) -> float:
    """
    Safely calculate the sum of a pandas Series.
    Invalid/non-numeric values are ignored.
    """

    if series is None:
        return 0.0

    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )

    if numeric.dropna().empty:
        return 0.0

    return float(numeric.sum())


def safe_ratio(
    numerator: pd.Series,
    denominator: pd.Series
) -> float:
    """
    Calculate the mean of row-level ratios.

    Example:
        renewable_energy / total_energy

    Rows with invalid or non-positive denominators
    are ignored.
    """

    numerator = pd.to_numeric(
        numerator,
        errors="coerce"
    )

    denominator = pd.to_numeric(
        denominator,
        errors="coerce"
    )

    valid = (
        (denominator > 0)
        & numerator.notna()
        & denominator.notna()
    )

    if not valid.any():
        return 0.0

    ratio = (
        numerator[valid]
        /
        denominator[valid]
    )

    ratio = ratio.replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna()

    if ratio.empty:
        return 0.0

    return float(ratio.mean())


def clean_group_value(
    value: Any
) -> str:
    """
    Clean sector and industry values.
    """

    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()

    if not value:
        return "Unknown"

    return value


# ============================================================
# PREPARE ANALYTICS DATA
# ============================================================

def prepare_analytics_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepare dataframe for analytics.

    Creates:

        Carbon_Intensity
        Renewable_Energy_Ratio
        NonRenewable_Energy_Ratio
        Energy_Per_Employee

    Carbon intensity:

        If XGBoost prediction exists:
            Predicted CO2 / Production

        Otherwise:
            Actual CO2 / Production
    """

    if not isinstance(
        df,
        pd.DataFrame
    ):
        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Dataset is empty."
        )

    result = df.copy()

    # ========================================================
    # CARBON INTENSITY
    # ========================================================
    #
    # If predictions exist, use predicted emissions.
    #
    # Otherwise, use the actual target from the dataset.
    #
    # This fixes the previous problem where Carbon_Intensity
    # was never created for the original dataset.
    # ========================================================

    if PRODUCTION_COLUMN in result.columns:

        production = pd.to_numeric(
            result[PRODUCTION_COLUMN],
            errors="coerce"
        )

        emissions = None

        # ----------------------------------------------------
        # Prefer XGBoost prediction.
        # ----------------------------------------------------

        if PREDICTION_COLUMN in result.columns:

            emissions = pd.to_numeric(
                result[PREDICTION_COLUMN],
                errors="coerce"
            )

        # ----------------------------------------------------
        # Otherwise use actual emissions.
        # ----------------------------------------------------

        elif ACTUAL_TARGET_COLUMN in result.columns:

            emissions = pd.to_numeric(
                result[ACTUAL_TARGET_COLUMN],
                errors="coerce"
            )

        # ----------------------------------------------------
        # Calculate carbon intensity.
        # ----------------------------------------------------

        if emissions is not None:

            result["Carbon_Intensity"] = np.where(
                (
                    (production > 0)
                    & production.notna()
                    & emissions.notna()
                ),
                emissions / production,
                np.nan
            )

    # ========================================================
    # RENEWABLE ENERGY RATIO
    # ========================================================

    if (
        TOTAL_ENERGY_COLUMN in result.columns
        and RENEWABLE_ENERGY_COLUMN in result.columns
    ):

        total_energy = pd.to_numeric(
            result[TOTAL_ENERGY_COLUMN],
            errors="coerce"
        )

        renewable_energy = pd.to_numeric(
            result[RENEWABLE_ENERGY_COLUMN],
            errors="coerce"
        )

        result["Renewable_Energy_Ratio"] = np.where(
            (
                (total_energy > 0)
                & total_energy.notna()
                & renewable_energy.notna()
            ),
            renewable_energy / total_energy,
            0.0
        )

    # ========================================================
    # NON-RENEWABLE ENERGY RATIO
    # ========================================================

    if (
        TOTAL_ENERGY_COLUMN in result.columns
        and NONRENEWABLE_ENERGY_COLUMN in result.columns
    ):

        total_energy = pd.to_numeric(
            result[TOTAL_ENERGY_COLUMN],
            errors="coerce"
        )

        nonrenewable_energy = pd.to_numeric(
            result[NONRENEWABLE_ENERGY_COLUMN],
            errors="coerce"
        )

        result["NonRenewable_Energy_Ratio"] = np.where(
            (
                (total_energy > 0)
                & total_energy.notna()
                & nonrenewable_energy.notna()
            ),
            nonrenewable_energy / total_energy,
            0.0
        )

    # ========================================================
    # ENERGY PER EMPLOYEE
    # ========================================================

    if (
        TOTAL_ENERGY_COLUMN in result.columns
        and EMPLOYMENT_COLUMN in result.columns
    ):

        total_energy = pd.to_numeric(
            result[TOTAL_ENERGY_COLUMN],
            errors="coerce"
        )

        employment = pd.to_numeric(
            result[EMPLOYMENT_COLUMN],
            errors="coerce"
        )

        result["Energy_Per_Employee"] = np.where(
            (
                (employment > 0)
                & employment.notna()
                & total_energy.notna()
            ),
            total_energy / employment,
            np.nan
        )

    return result


# ============================================================
# SUMMARIZE GROUP
# ============================================================

def summarize_group(
    group: pd.DataFrame,
    group_name: str,
    group_value: str
) -> Dict[str, Any]:
    """
    Generate analytics for one group.

    group_name:
        overall
        sector
        industry
    """

    summary = {
        "name": group_value,
        "records": int(len(group)),

        "total_emissions": 0.0,
        "average_emissions": 0.0,

        "average_energy_consumption": 0.0,

        "average_renewable_energy": 0.0,
        "average_nonrenewable_energy": 0.0,

        "average_renewable_share": 0.0,
        "average_nonrenewable_share": 0.0,

        "average_production": 0.0,

        "average_transport_distance": 0.0,

        "average_raw_material_usage": 0.0,

        "average_employment": 0.0,

        "average_carbon_intensity": 0.0,

        "average_energy_per_employee": 0.0,
    }

    # ========================================================
    # EMISSIONS
    # ========================================================

    if PREDICTION_COLUMN in group.columns:

        emissions_column = PREDICTION_COLUMN

    elif ACTUAL_TARGET_COLUMN in group.columns:

        emissions_column = ACTUAL_TARGET_COLUMN

    else:

        emissions_column = None

    if emissions_column is not None:

        summary["total_emissions"] = safe_sum(
            group[emissions_column]
        )

        summary["average_emissions"] = safe_mean(
            group[emissions_column]
        )

    # ========================================================
    # ENERGY
    # ========================================================

    if TOTAL_ENERGY_COLUMN in group.columns:

        summary["average_energy_consumption"] = safe_mean(
            group[TOTAL_ENERGY_COLUMN]
        )

    # ========================================================
    # RENEWABLE ENERGY
    # ========================================================

    if RENEWABLE_ENERGY_COLUMN in group.columns:

        summary["average_renewable_energy"] = safe_mean(
            group[RENEWABLE_ENERGY_COLUMN]
        )

    # ========================================================
    # NON-RENEWABLE ENERGY
    # ========================================================

    if NONRENEWABLE_ENERGY_COLUMN in group.columns:

        summary["average_nonrenewable_energy"] = safe_mean(
            group[NONRENEWABLE_ENERGY_COLUMN]
        )

    # ========================================================
    # RENEWABLE SHARE
    # ========================================================

    if (
        RENEWABLE_ENERGY_COLUMN in group.columns
        and TOTAL_ENERGY_COLUMN in group.columns
    ):

        summary["average_renewable_share"] = safe_ratio(
            group[RENEWABLE_ENERGY_COLUMN],
            group[TOTAL_ENERGY_COLUMN]
        )

    # ========================================================
    # NON-RENEWABLE SHARE
    # ========================================================

    if (
        NONRENEWABLE_ENERGY_COLUMN in group.columns
        and TOTAL_ENERGY_COLUMN in group.columns
    ):

        summary["average_nonrenewable_share"] = safe_ratio(
            group[NONRENEWABLE_ENERGY_COLUMN],
            group[TOTAL_ENERGY_COLUMN]
        )

    # ========================================================
    # PRODUCTION
    # ========================================================

    if PRODUCTION_COLUMN in group.columns:

        summary["average_production"] = safe_mean(
            group[PRODUCTION_COLUMN]
        )

    # ========================================================
    # TRANSPORT
    # ========================================================

    if TRANSPORT_COLUMN in group.columns:

        summary["average_transport_distance"] = safe_mean(
            group[TRANSPORT_COLUMN]
        )

    # ========================================================
    # RAW MATERIAL
    # ========================================================

    if RAW_MATERIAL_COLUMN in group.columns:

        summary["average_raw_material_usage"] = safe_mean(
            group[RAW_MATERIAL_COLUMN]
        )

    # ========================================================
    # EMPLOYMENT
    # ========================================================

    if EMPLOYMENT_COLUMN in group.columns:

        summary["average_employment"] = safe_mean(
            group[EMPLOYMENT_COLUMN]
        )

    # ========================================================
    # CARBON INTENSITY
    # ========================================================

    if "Carbon_Intensity" in group.columns:

        summary["average_carbon_intensity"] = safe_mean(
            group["Carbon_Intensity"]
        )

    # ========================================================
    # ENERGY PER EMPLOYEE
    # ========================================================

    if "Energy_Per_Employee" in group.columns:

        summary["average_energy_per_employee"] = safe_mean(
            group["Energy_Per_Employee"]
        )

    return summary


# ============================================================
# OVERALL SUMMARY
# ============================================================

def calculate_overall_summary(
    df: pd.DataFrame
) -> Dict[str, Any]:

    return summarize_group(
        group=df,
        group_name="overall",
        group_value="Overall"
    )


# ============================================================
# SECTOR SUMMARY
# ============================================================

def calculate_sector_summary(
    df: pd.DataFrame
) -> List[Dict[str, Any]]:

    if SECTOR_COLUMN not in df.columns:
        return []

    working_df = df.copy()

    working_df[SECTOR_COLUMN] = (
        working_df[SECTOR_COLUMN]
        .apply(clean_group_value)
    )

    results = []

    for sector, group in working_df.groupby(
        SECTOR_COLUMN,
        dropna=False
    ):

        results.append(
            summarize_group(
                group=group,
                group_name="sector",
                group_value=str(sector)
            )
        )

    # Sort by average emissions descending.
    results.sort(
        key=lambda item: item["average_emissions"],
        reverse=True
    )

    return results


# ============================================================
# INDUSTRY SUMMARY
# ============================================================

def calculate_industry_summary(
    df: pd.DataFrame
) -> List[Dict[str, Any]]:

    if INDUSTRY_COLUMN not in df.columns:
        return []

    working_df = df.copy()

    working_df[INDUSTRY_COLUMN] = (
        working_df[INDUSTRY_COLUMN]
        .apply(clean_group_value)
    )

    results = []

    for industry, group in working_df.groupby(
        INDUSTRY_COLUMN,
        dropna=False
    ):

        results.append(
            summarize_group(
                group=group,
                group_name="industry",
                group_value=str(industry)
            )
        )

    results.sort(
        key=lambda item: item["average_emissions"],
        reverse=True
    )

    return results


# ============================================================
# SECTOR + INDUSTRY HIERARCHY
# ============================================================

def calculate_sector_industry_summary(
    df: pd.DataFrame
) -> List[Dict[str, Any]]:

    if SECTOR_COLUMN not in df.columns:
        return []

    if INDUSTRY_COLUMN not in df.columns:
        return []

    working_df = df.copy()

    working_df[SECTOR_COLUMN] = (
        working_df[SECTOR_COLUMN]
        .apply(clean_group_value)
    )

    working_df[INDUSTRY_COLUMN] = (
        working_df[INDUSTRY_COLUMN]
        .apply(clean_group_value)
    )

    results = []

    for sector, sector_group in working_df.groupby(
        SECTOR_COLUMN,
        dropna=False
    ):

        industries = []

        for industry, industry_group in sector_group.groupby(
            INDUSTRY_COLUMN,
            dropna=False
        ):

            industries.append(
                summarize_group(
                    group=industry_group,
                    group_name="industry",
                    group_value=str(industry)
                )
            )

        industries.sort(
            key=lambda item: item["average_emissions"],
            reverse=True
        )

        results.append(
            {
                "sector": str(sector),
                "records": int(len(sector_group)),
                "industries": industries,
            }
        )

    return results


# ============================================================
# COMPLETE ANALYTICS
# ============================================================

def calculate_all_analytics(
    df: pd.DataFrame
) -> Dict[str, Any]:

    if not isinstance(
        df,
        pd.DataFrame
    ):
        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Dataset is empty."
        )

    working_df = prepare_analytics_data(
        df
    )

    return {
        "overall": calculate_overall_summary(
            working_df
        ),

        "sectors": calculate_sector_summary(
            working_df
        ),

        "industries": calculate_industry_summary(
            working_df
        ),

        "sector_industry": calculate_sector_industry_summary(
            working_df
        ),

        "total_records": int(
            len(working_df)
        ),
    }


# ============================================================
# DATASET ANALYTICS REPORT
# ============================================================

def print_analytics_report(
    analytics: Dict[str, Any]
) -> None:

    print("\n" + "=" * 70)

    print(
        "CARBON AI - SECTOR ANALYTICS REPORT"
    )

    print("=" * 70)

    # ========================================================
    # OVERALL
    # ========================================================

    overall = analytics["overall"]

    print(
        "\nOVERALL DATASET"
    )

    print(
        f"Records: "
        f"{overall['records']}"
    )

    print(
        f"Total emissions: "
        f"{overall['total_emissions']:.4f} tCO2e"
    )

    print(
        f"Average emissions: "
        f"{overall['average_emissions']:.4f} tCO2e"
    )

    print(
        f"Average energy: "
        f"{overall['average_energy_consumption']:.2f} kWh"
    )

    print(
        f"Average renewable share: "
        f"{overall['average_renewable_share'] * 100:.2f}%"
    )

    print(
        f"Average non-renewable share: "
        f"{overall['average_nonrenewable_share'] * 100:.2f}%"
    )

    print(
        f"Average production: "
        f"{overall['average_production']:.2f}"
    )

    print(
        f"Average carbon intensity: "
        f"{overall['average_carbon_intensity']:.6f} "
        f"tCO2e/unit"
    )

    print(
        f"Average energy per employee: "
        f"{overall['average_energy_per_employee']:.2f} "
        f"kWh/employee"
    )

    # ========================================================
    # SECTORS
    # ========================================================

    sectors = analytics["sectors"]

    print(
        "\nSECTOR SUMMARY"
    )

    print(
        "-" * 70
    )

    for sector in sectors:

        print(
            f"\n{sector['name']}"
        )

        print(
            f"  Records: "
            f"{sector['records']}"
        )

        print(
            f"  Total emissions: "
            f"{sector['total_emissions']:.2f} tCO2e"
        )

        print(
            f"  Average emissions: "
            f"{sector['average_emissions']:.2f} tCO2e"
        )

        print(
            f"  Average energy: "
            f"{sector['average_energy_consumption']:.2f} kWh"
        )

        print(
            f"  Renewable share: "
            f"{sector['average_renewable_share'] * 100:.2f}%"
        )

        print(
            f"  Non-renewable share: "
            f"{sector['average_nonrenewable_share'] * 100:.2f}%"
        )

        print(
            f"  Average production: "
            f"{sector['average_production']:.2f}"
        )

        print(
            f"  Average transport: "
            f"{sector['average_transport_distance']:.2f} km"
        )

        print(
            f"  Average raw material: "
            f"{sector['average_raw_material_usage']:.2f} kg"
        )

        print(
            f"  Average employment: "
            f"{sector['average_employment']:.2f}"
        )

        print(
            f"  Carbon intensity: "
            f"{sector['average_carbon_intensity']:.6f} "
            f"tCO2e/unit"
        )

        print(
            f"  Energy per employee: "
            f"{sector['average_energy_per_employee']:.2f} "
            f"kWh/employee"
        )

    # ========================================================
    # INDUSTRIES
    # ========================================================

    industries = analytics["industries"]

    print(
        "\nINDUSTRY SUMMARY"
    )

    print(
        "-" * 70
    )

    for industry in industries:

        print(
            f"{industry['name']}: "
            f"{industry['average_emissions']:.2f} tCO2e "
            f"average, "
            f"{industry['records']} records, "
            f"carbon intensity "
            f"{industry['average_carbon_intensity']:.6f} "
            f"tCO2e/unit"
        )

    # ========================================================
    # SECTOR + INDUSTRY
    # ========================================================

    sector_industry = analytics[
        "sector_industry"
    ]

    print(
        "\nSECTOR + INDUSTRY SUMMARY"
    )

    print(
        "-" * 70
    )

    for sector_data in sector_industry:

        print(
            f"\nSector: "
            f"{sector_data['sector']}"
        )

        print(
            f"Records: "
            f"{sector_data['records']}"
        )

        for industry in sector_data["industries"]:

            print(
                f"  {industry['name']}: "
                f"{industry['average_emissions']:.2f} tCO2e "
                f"average, "
                f"{industry['records']} records, "
                f"carbon intensity "
                f"{industry['average_carbon_intensity']:.6f} "
                f"tCO2e/unit"
            )

    print(
        "\n" + "=" * 70
    )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    import os

    DATASET_PATH = (
        "carbon_emission_dataset_with_Industry.csv"
    )

    if not os.path.exists(
        DATASET_PATH
    ):

        print(
            f"Dataset not found: "
            f"{DATASET_PATH}"
        )

        print(
            "\nRun this file from the backend directory."
        )

        raise SystemExit(1)

    print(
        "\nLoading dataset..."
    )

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Dataset loaded: "
        f"{df.shape}"
    )

    analytics = calculate_all_analytics(
        df
    )

    print_analytics_report(
        analytics
    )

    print(
        "\nSector analytics completed successfully. 🚀"
    )