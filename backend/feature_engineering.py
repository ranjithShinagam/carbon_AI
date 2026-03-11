def calculate_post_prediction_features(predicted_co2: float, production_output: float, total_energy: float, employment_count: float):
    # Protect against divide-by-zero errors
    production_output = max(production_output, 1.0)
    employment_count = max(employment_count, 1.0)
    
    carbon_intensity = predicted_co2 / production_output
    energy_per_employee = total_energy / employment_count
    
    return {
        "carbon_intensity": carbon_intensity,
        "energy_per_employee": energy_per_employee
    }
