def calculate_post_prediction_features(
    predicted_co2: float,
    production_output: float,
    total_energy: float,
    employment_count: float,
    renewable_energy: float = 0.0,
    nonrenewable_energy: float = 0.0
):
    """
    Calculate useful metrics after carbon emission prediction.
    """

    # Avoid division by zero
    safe_production = max(production_output, 1.0)
    safe_employment = max(employment_count, 1.0)
    safe_total_energy = max(total_energy, 0.0)

    # Carbon emitted per production unit
    carbon_intensity = predicted_co2 / safe_production

    # Energy consumed per employee
    energy_per_employee = safe_total_energy / safe_employment

    # Energy shares
    if safe_total_energy > 0:
        renewable_energy_ratio = renewable_energy / safe_total_energy
        nonrenewable_energy_ratio = nonrenewable_energy / safe_total_energy
    else:
        renewable_energy_ratio = 0.0
        nonrenewable_energy_ratio = 0.0

    return {
        "carbon_intensity": carbon_intensity,
        "energy_per_employee": energy_per_employee,
        "renewable_energy_ratio": renewable_energy_ratio,
        "nonrenewable_energy_ratio": nonrenewable_energy_ratio
    }