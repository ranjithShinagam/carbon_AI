# ============================================================
# Carbon AI - Dataset Adapter
# ============================================================
# Purpose:
#   Convert user-uploaded CSV datasets with different column
#   names into the canonical schema expected by Carbon AI.
#
# Important design:
#   - Required model features MUST be present.
#   - Extra columns are allowed and preserved.
#   - Exact matches are preferred.
#   - Explicit aliases are preferred over fuzzy matching.
#   - Fuzzy matching is only used to resolve missing
#     required model features.
# ============================================================

import re
import sys
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# ============================================================
# CANONICAL COLUMN NAMES
# ============================================================

CANONICAL_COLUMNS = {
    "total_energy": "Total_Energy_Consumption_kWh",
    "renewable_energy": "Renewable_Energy_Consumption_kWh",
    "nonrenewable_energy": "NonRenewable_Energy_Consumption_kWh",
    "production_output": "Production_Output_Units",
    "transport_distance": "Supply_Chain_Transport_km",
    "raw_material_usage": "Raw_Material_Usage_kg",
    "employment_count": "Employment_Count",
    "sector": "Sector",
    "target": "Carbon_Emission_tCO2e_TARGET",
}


# ============================================================
# REQUIRED MODEL FEATURES
# ============================================================

REQUIRED_MODEL_COLUMNS = [
    "Total_Energy_Consumption_kWh",
    "NonRenewable_Energy_Consumption_kWh",
    "Renewable_Energy_Consumption_kWh",
    "Production_Output_Units",
    "Supply_Chain_Transport_km",
    "Raw_Material_Usage_kg",
    "Employment_Count",
]


# ============================================================
# OPTIONAL ANALYTICS COLUMNS
# ============================================================

OPTIONAL_COLUMNS = [
    "Sector",
    "Carbon_Emission_tCO2e_TARGET",
]


# ============================================================
# COLUMN ALIASES
# ============================================================
# Explicit aliases are safer than relying completely on
# fuzzy matching.
# ============================================================

COLUMN_ALIASES = {

    "Total_Energy_Consumption_kWh": [
        "total_energy",
        "total_energy_consumption",
        "total_energy_consumption_kwh",
        "energy_consumption",
        "energy_consumption_kwh",
        "total_energy_kwh",
        "electricity",
        "electricity_consumption",
        "electricity_consumption_kwh",
        "energy_used",
        "total_energy_used",
        "energy",
    ],

    "Renewable_Energy_Consumption_kWh": [
        "renewable_energy",
        "renewable_energy_consumption",
        "renewable_energy_consumption_kwh",
        "renewable_energy_kwh",
        "renewable_consumption",
        "renewable_consumption_kwh",
        "re_consumption",
        "renewable",
        "green_energy",
        "clean_energy",
    ],

    "NonRenewable_Energy_Consumption_kWh": [
        "nonrenewable_energy",
        "non_renewable_energy",
        "nonrenewable_energy_consumption",
        "nonrenewable_energy_consumption_kwh",
        "non_renewable_energy_consumption_kwh",
        "nonrenewable_energy_kwh",
        "non_renewable_energy_kwh",
        "nre_consumption",
        "nre_consumption_kwh",
        "nonrenewable_consumption",
        "non_renewable_consumption",
        "fossil_energy",
        "fossil_fuel_energy",
    ],

    "Production_Output_Units": [
        "production",
        "production_output",
        "production_output_units",
        "production_units",
        "output",
        "output_units",
        "units_produced",
        "production_volume",
        "manufacturing_output",
    ],

    "Supply_Chain_Transport_km": [
        "transport_km",
        "transport_distance",
        "transport_distance_km",
        "supply_chain_transport",
        "supply_chain_transport_km",
        "supply_chain_distance",
        "transport",
        "distance",
        "distance_km",
        "logistics_distance",
        "shipping_distance",
    ],

    "Raw_Material_Usage_kg": [
        "raw_material",
        "raw_material_usage",
        "raw_material_usage_kg",
        "raw_material_kg",
        "material_usage",
        "material_usage_kg",
        "materials_used",
        "materials_used_kg",
        "raw_material_consumption",
    ],

    "Employment_Count": [
        "employment",
        "employment_count",
        "employee_count",
        "employees",
        "employees_count",
        "number_of_employees",
        "num_employees",
        "staff_count",
        "workforce",
        "workers",
        "employee",
    ],

    "Sector": [
        "sector",
        "industry",
        "industry_type",
        "industry_sector",
        "industry_sectors",
        "business_sector",
        "business_type",
        "company_sector",
        "company_industry",
        "industry_name",
    ],

    "Carbon_Emission_tCO2e_TARGET": [
        "target",
        "carbon_emission",
        "carbon_emissions",
        "carbon_emission_tco2e",
        "carbon_emission_tco2e_target",
        "carbon_emissions_tco2e",
        "emissions",
        "emission",
        "co2_emission",
        "co2_emissions",
        "co2e",
        "carbon_output",
    ],
}


# ============================================================
# FUZZY MATCHING SETTINGS
# ============================================================

FUZZY_THRESHOLD = 0.78

# If two possible matches are extremely close,
# we don't automatically select one.
AMBIGUITY_MARGIN = 0.05


# ============================================================
# BUILD ALIAS MAP
# ============================================================

def build_alias_map() -> Dict[str, str]:
    """
    Build:

        normalized_alias -> canonical_column
    """

    alias_map = {}

    for canonical_column, aliases in COLUMN_ALIASES.items():

        # Canonical column itself
        normalized_canonical = normalize_column_name(
            canonical_column
        )

        alias_map[
            normalized_canonical
        ] = canonical_column

        # Explicit aliases
        for alias in aliases:

            normalized_alias = normalize_column_name(
                alias
            )

            alias_map[
                normalized_alias
            ] = canonical_column

    return alias_map


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column_name(
    column_name: str
) -> str:
    """
    Normalize a column name.

    Examples:

        "Total Energy Consumption (kWh)"
            ->
        "total_energy_consumption_kwh"

        "NRE Consumption"
            ->
        "nre_consumption"
    """

    value = str(column_name).strip().lower()

    # Common symbols
    value = value.replace("%", " percent ")
    value = value.replace("²", "2")

    # Replace everything except letters/numbers
    # with spaces.
    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value
    )

    # Remove repeated spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    # Convert spaces to underscores
    value = value.replace(
        " ",
        "_"
    )

    return value


# Build after normalize_column_name is defined.
ALIAS_MAP = build_alias_map()


# ============================================================
# SIMILARITY
# ============================================================

def similarity_score(
    value1: str,
    value2: str
) -> float:

    return SequenceMatcher(
        None,
        normalize_column_name(value1),
        normalize_column_name(value2)
    ).ratio()


# ============================================================
# EXACT MATCH
# ============================================================

def find_exact_match(
    uploaded_column: str
):
    """
    Find exact canonical/alias match.
    """

    normalized = normalize_column_name(
        uploaded_column
    )

    return ALIAS_MAP.get(
        normalized
    )


# ============================================================
# FUZZY MATCH FOR A SPECIFIC REQUIRED COLUMN
# ============================================================

def find_fuzzy_match_for_required_column(
    uploaded_columns: List[str],
    required_column: str
) -> Dict:

    candidates = []

    aliases = COLUMN_ALIASES.get(
        required_column,
        []
    )

    comparison_names = [
        required_column
    ] + aliases

    for uploaded_column in uploaded_columns:

        best_column_score = 0.0

        for comparison_name in comparison_names:

            score = similarity_score(
                uploaded_column,
                comparison_name
            )

            best_column_score = max(
                best_column_score,
                score
            )

        candidates.append(
            (
                uploaded_column,
                best_column_score
            )
        )

    if not candidates:

        return {
            "canonical_column": None,
            "uploaded_column": None,
            "score": 0.0,
            "match_type": "unmatched",
            "needs_confirmation": True,
        }

    candidates.sort(
        key=lambda item: item[1],
        reverse=True
    )

    best_column, best_score = candidates[0]

    second_score = (
        candidates[1][1]
        if len(candidates) > 1
        else 0.0
    )

    # Too weak
    if best_score < FUZZY_THRESHOLD:

        return {
            "canonical_column": None,
            "uploaded_column": best_column,
            "score": round(
                best_score,
                4
            ),
            "match_type": "low_confidence",
            "needs_confirmation": True,
        }

    # Ambiguous
    if (
        second_score >= FUZZY_THRESHOLD
        and (
            best_score - second_score
        ) < AMBIGUITY_MARGIN
    ):

        return {
            "canonical_column": None,
            "uploaded_column": best_column,
            "score": round(
                best_score,
                4
            ),
            "match_type": "ambiguous",
            "needs_confirmation": True,
        }

    return {
        "canonical_column": required_column,
        "uploaded_column": best_column,
        "score": round(
            best_score,
            4
        ),
        "match_type": "fuzzy",
        "needs_confirmation": False,
    }


# ============================================================
# MAP DATASET COLUMNS
# ============================================================

def map_columns(
    df: pd.DataFrame
) -> Dict:

    mapping = {}

    # Keep track of canonical columns already mapped.
    used_canonical_columns = set()

    # Columns that were not mapped because they are
    # irrelevant to the model.
    ignored_columns = []

    # --------------------------------------------------------
    # STEP 1
    # Exact canonical/alias matches first.
    # --------------------------------------------------------

    for uploaded_column in df.columns:

        canonical_column = find_exact_match(
            uploaded_column
        )

        if canonical_column is None:
            continue

        # Don't let a second column overwrite
        # the first exact match.
        if canonical_column in used_canonical_columns:

            ignored_columns.append(
                uploaded_column
            )

            continue

        mapping[
            uploaded_column
        ] = canonical_column

        used_canonical_columns.add(
            canonical_column
        )

    # --------------------------------------------------------
    # STEP 2
    # Find which REQUIRED columns are still missing.
    # --------------------------------------------------------

    missing_required_columns = [
        column
        for column in REQUIRED_MODEL_COLUMNS
        if column not in used_canonical_columns
    ]

    # --------------------------------------------------------
    # STEP 3
    # Fuzzy matching ONLY for missing required columns.
    # --------------------------------------------------------

    fuzzy_issues = []

    available_columns = [
        column
        for column in df.columns
        if column not in mapping
    ]

    for required_column in missing_required_columns:

        result = find_fuzzy_match_for_required_column(
            available_columns,
            required_column
        )

        # ----------------------------------------------------
        # Good fuzzy match
        # ----------------------------------------------------

        if (
            result["canonical_column"]
            is not None
        ):

            uploaded_column = result[
                "uploaded_column"
            ]

            # Prevent same uploaded column
            # from mapping to multiple features.
            if uploaded_column in mapping:

                fuzzy_issues.append({
                    "required_column": required_column,
                    "uploaded_column": uploaded_column,
                    "score": result["score"],
                    "match_type": "duplicate_candidate",
                    "needs_confirmation": True,
                })

                continue

            mapping[
                uploaded_column
            ] = required_column

            used_canonical_columns.add(
                required_column
            )

            available_columns.remove(
                uploaded_column
            )

        # ----------------------------------------------------
        # Could not confidently map
        # ----------------------------------------------------

        else:

            fuzzy_issues.append({
                "required_column": required_column,
                "uploaded_column": result[
                    "uploaded_column"
                ],
                "score": result[
                    "score"
                ],
                "match_type": result[
                    "match_type"
                ],
                "needs_confirmation": True,
            })

    # --------------------------------------------------------
    # STEP 4
    # All remaining columns are simply extra columns.
    # --------------------------------------------------------

    mapped_uploaded_columns = set(
        mapping.keys()
    )

    for column in df.columns:

        if column not in mapped_uploaded_columns:

            ignored_columns.append(
                column
            )

    return {
        "mapping": mapping,
        "issues": fuzzy_issues,
        "ignored_columns": ignored_columns,
    }


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

def validate_required_columns(
    mapping: Dict[str, str]
) -> Dict:

    mapped_columns = set(
        mapping.values()
    )

    missing = [
        column
        for column in REQUIRED_MODEL_COLUMNS
        if column not in mapped_columns
    ]

    return {
        "valid": len(missing) == 0,
        "missing_columns": missing,
    }


# ============================================================
# RENAME TO CANONICAL SCHEMA
# ============================================================

def rename_to_canonical(
    df: pd.DataFrame,
    mapping: Dict[str, str]
) -> pd.DataFrame:

    rename_map = {
        uploaded_column: canonical_column
        for uploaded_column, canonical_column
        in mapping.items()
    }

    return df.rename(
        columns=rename_map
    )


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_numeric_columns(
    df: pd.DataFrame
) -> Dict:

    errors = []

    for column in REQUIRED_MODEL_COLUMNS:

        if column not in df.columns:
            continue

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        original_non_null = (
            df[column].notna()
        )

        invalid_values = (
            converted.isna()
            & original_non_null
        ).sum()

        if invalid_values > 0:

            errors.append({
                "column": column,
                "invalid_values": int(
                    invalid_values
                ),
            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

def convert_numeric_columns(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    for column in REQUIRED_MODEL_COLUMNS:

        if column not in df.columns:
            continue

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# ============================================================
# NEGATIVE VALUE VALIDATION
# ============================================================

def validate_negative_values(
    df: pd.DataFrame
) -> Dict:

    errors = []

    for column in REQUIRED_MODEL_COLUMNS:

        if column not in df.columns:
            continue

        negative_count = (
            df[column] < 0
        ).sum()

        if negative_count > 0:

            errors.append({
                "column": column,
                "negative_values": int(
                    negative_count
                ),
            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


# ============================================================
# ENERGY CONSISTENCY VALIDATION
# ============================================================

def validate_energy_consistency(
    df: pd.DataFrame,
    tolerance: float = 0.01
) -> Dict:

    required_columns = [
        "Total_Energy_Consumption_kWh",
        "Renewable_Energy_Consumption_kWh",
        "NonRenewable_Energy_Consumption_kWh",
    ]

    if not all(
        column in df.columns
        for column in required_columns
    ):

        return {
            "valid": True,
            "checked": False,
            "message": (
                "Energy consistency could not "
                "be checked."
            ),
        }

    total_energy = df[
        "Total_Energy_Consumption_kWh"
    ]

    renewable_energy = df[
        "Renewable_Energy_Consumption_kWh"
    ]

    nonrenewable_energy = df[
        "NonRenewable_Energy_Consumption_kWh"
    ]

    expected_total = (
        renewable_energy
        + nonrenewable_energy
    )

    difference = (
        total_energy
        - expected_total
    ).abs()

    inconsistent_rows = (
        difference > tolerance
    ).sum()

    return {
        "valid": inconsistent_rows == 0,
        "checked": True,
        "inconsistent_rows": int(
            inconsistent_rows
        ),
        "max_difference": float(
            difference.max()
        ),
        "median_difference": float(
            difference.median()
        ),
    }


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def add_engineered_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    total_energy = df[
        "Total_Energy_Consumption_kWh"
    ]

    nonrenewable_energy = df[
        "NonRenewable_Energy_Consumption_kWh"
    ]

    df[
        "NonRenewable_Energy_Ratio"
    ] = np.where(
        total_energy > 0,
        nonrenewable_energy / total_energy,
        0.0
    )

    return df


# ============================================================
# COMPLETE DATASET ADAPTER
# ============================================================

def adapt_dataset(
    df: pd.DataFrame,
    strict: bool = True
) -> Dict:

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    if df.empty:

        return {
            "success": False,
            "stage": "empty_dataset",
            "message": (
                "Uploaded dataset is empty."
            ),
        }

    # --------------------------------------------------------
    # Remove completely empty columns
    # --------------------------------------------------------

    df = df.dropna(
        axis=1,
        how="all"
    )

    # --------------------------------------------------------
    # Remove duplicate rows
    # --------------------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    df = df.drop_duplicates().reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Map columns
    # --------------------------------------------------------

    mapping_result = map_columns(
        df
    )

    mapping = mapping_result[
        "mapping"
    ]

    issues = mapping_result[
        "issues"
    ]

    ignored_columns = mapping_result[
        "ignored_columns"
    ]

    # --------------------------------------------------------
    # Validate required model features
    # --------------------------------------------------------

    required_result = validate_required_columns(
        mapping
    )

    if not required_result["valid"]:

        return {
            "success": False,
            "stage": "column_validation",
            "message": (
                "Dataset does not contain all "
                "required model features."
            ),
            "mapping": mapping,
            "issues": issues,
            "ignored_columns": ignored_columns,
            "missing_columns": required_result[
                "missing_columns"
            ],
        }

    # --------------------------------------------------------
    # If fuzzy matching found an uncertainty
    # --------------------------------------------------------

    if strict and issues:

        return {
            "success": False,
            "stage": "column_mapping",
            "message": (
                "Some required model columns "
                "could not be mapped confidently."
            ),
            "mapping": mapping,
            "issues": issues,
            "ignored_columns": ignored_columns,
            "missing_columns": required_result[
                "missing_columns"
            ],
        }

    # --------------------------------------------------------
    # Rename mapped columns
    # --------------------------------------------------------

    adapted_df = rename_to_canonical(
        df,
        mapping
    )

    # --------------------------------------------------------
    # Numeric validation
    # --------------------------------------------------------

    numeric_result = validate_numeric_columns(
        adapted_df
    )

    if not numeric_result["valid"]:

        return {
            "success": False,
            "stage": "numeric_validation",
            "message": (
                "Some required model columns "
                "contain invalid numeric values."
            ),
            "mapping": mapping,
            "issues": numeric_result[
                "errors"
            ],
            "ignored_columns": ignored_columns,
        }

    # Convert values
    adapted_df = convert_numeric_columns(
        adapted_df
    )

    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    missing_value_report = {}

    for column in REQUIRED_MODEL_COLUMNS:

        missing_count = int(
            adapted_df[column].isna().sum()
        )

        if missing_count > 0:

            missing_value_report[
                column
            ] = missing_count

    # Prediction input should not contain missing
    # model features.
    if missing_value_report:

        return {
            "success": False,
            "stage": "missing_values",
            "message": (
                "Required model features contain "
                "missing values."
            ),
            "mapping": mapping,
            "issues": missing_value_report,
            "ignored_columns": ignored_columns,
        }

    # --------------------------------------------------------
    # Negative values
    # --------------------------------------------------------

    negative_result = validate_negative_values(
        adapted_df
    )

    if not negative_result["valid"]:

        return {
            "success": False,
            "stage": "value_validation",
            "message": (
                "Negative values were found in "
                "model features."
            ),
            "mapping": mapping,
            "issues": negative_result[
                "errors"
            ],
            "ignored_columns": ignored_columns,
        }

    # --------------------------------------------------------
    # Energy consistency
    # --------------------------------------------------------

    energy_result = validate_energy_consistency(
        adapted_df
    )

    energy_warning = None

    if (
        energy_result.get("checked")
        and not energy_result.get("valid")
    ):

        energy_warning = (
            "Total energy does not exactly equal "
            "renewable + non-renewable energy "
            "for some rows."
        )

    # --------------------------------------------------------
    # Feature engineering
    # --------------------------------------------------------

    adapted_df = add_engineered_features(
        adapted_df
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "success": True,
        "stage": "completed",

        "data": adapted_df,

        "mapping": mapping,

        "issues": issues,

        "ignored_columns": ignored_columns,

        "energy_validation": energy_result,

        "energy_warning": energy_warning,

        "duplicate_rows_removed": duplicate_count,

        "rows": len(adapted_df),

        "columns": list(
            adapted_df.columns
        ),
    }


# ============================================================
# CSV ADAPTER
# ============================================================

def adapt_csv(
    file_path: str,
    strict: bool = True
) -> Dict:

    try:

        df = pd.read_csv(
            file_path
        )

    except Exception as exc:

        return {
            "success": False,
            "stage": "file_read",
            "message": (
                f"Could not read CSV file: {exc}"
            ),
        }

    return adapt_dataset(
        df,
        strict=strict
    )


# ============================================================
# PRINT REPORT
# ============================================================

def print_mapping_report(
    result: Dict
) -> None:

    print("\n" + "=" * 70)

    print(
        "CARBON AI - DATASET ADAPTER REPORT"
    )

    print("=" * 70)

    print(
        f"\nSuccess: "
        f"{result.get('success')}"
    )

    print(
        f"Stage: "
        f"{result.get('stage')}"
    )

    # --------------------------------------------------------
    # Mapping
    # --------------------------------------------------------

    mapping = result.get(
        "mapping",
        {}
    )

    if mapping:

        print(
            "\nColumn Mapping:"
        )

        for uploaded, canonical in mapping.items():

            print(
                f"  {uploaded}"
                f"  -->  "
                f"{canonical}"
            )

    # --------------------------------------------------------
    # Ignored columns
    # --------------------------------------------------------

    ignored = result.get(
        "ignored_columns",
        []
    )

    if ignored:

        print(
            "\nExtra / ignored columns:"
        )

        for column in ignored:

            print(
                f"  - {column}"
            )

    # --------------------------------------------------------
    # Issues
    # --------------------------------------------------------

    issues = result.get(
        "issues",
        []
    )

    if issues:

        print(
            "\nIssues:"
        )

        for issue in issues:

            print(
                f"  {issue}"
            )

    # --------------------------------------------------------
    # Missing columns
    # --------------------------------------------------------

    missing = result.get(
        "missing_columns",
        []
    )

    if missing:

        print(
            "\nMissing required columns:"
        )

        for column in missing:

            print(
                f"  - {column}"
            )

    # --------------------------------------------------------
    # Energy validation
    # --------------------------------------------------------

    energy_validation = result.get(
        "energy_validation"
    )

    if energy_validation:

        print(
            "\nEnergy validation:"
        )

        print(
            f"  Checked: "
            f"{energy_validation.get('checked')}"
        )

        print(
            f"  Valid: "
            f"{energy_validation.get('valid')}"
        )

        if energy_validation.get(
            "checked"
        ):

            print(
                f"  Inconsistent rows: "
                f"{energy_validation.get('inconsistent_rows')}"
            )

            print(
                f"  Maximum difference: "
                f"{energy_validation.get('max_difference')}"
            )

            print(
                f"  Median difference: "
                f"{energy_validation.get('median_difference')}"
            )

    # --------------------------------------------------------
    # Energy warning
    # --------------------------------------------------------

    if result.get(
        "energy_warning"
    ):

        print(
            "\nWARNING:"
        )

        print(
            f"  {result['energy_warning']}"
        )

    # --------------------------------------------------------
    # Dataset information
    # --------------------------------------------------------

    if result.get(
        "duplicate_rows_removed"
    ) is not None:

        print(
            "\nDuplicate rows removed: "
            f"{result['duplicate_rows_removed']}"
        )

    if result.get(
        "rows"
    ) is not None:

        print(
            "Rows after processing: "
            f"{result['rows']}"
        )

    print(
        "\n" + "=" * 70
    )


# ============================================================
# DIRECT COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python dataset_adapter.py "
            "<csv_file>"
        )

        print(
            "\nExample:"
        )

        print(
            "python dataset_adapter.py "
            "carbon_emission_dataset_with_Industry.csv"
        )

        sys.exit(1)

    file_path = sys.argv[1]

    result = adapt_csv(
        file_path
    )

    print_mapping_report(
        result
    )

    # --------------------------------------------------------
    # Show adapted dataset if successful
    # --------------------------------------------------------

    if result.get("success"):

        adapted_df = result[
            "data"
        ]

        print(
            "\nFinal dataset shape:"
        )

        print(
            adapted_df.shape
        )

        print(
            "\nFinal columns:"
        )

        for column in adapted_df.columns:

            print(
                f" - {column}"
            )

        print(
            "\nFirst 5 rows:"
        )

        print(
            adapted_df.head()
        )

        print(
            "\nDataset adaptation "
            "completed successfully. 🚀"
        )

    else:

        print(
            "\nDataset adaptation failed."
        )

        print(
            "Fix the reported issue before "
            "using this dataset for prediction."
        )