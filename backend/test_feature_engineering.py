from feature_engineering import calculate_post_prediction_features


result = calculate_post_prediction_features(
    predicted_co2=41.7442,
    production_output=10000,
    total_energy=50000,
    employment_count=100,
    renewable_energy=15000,
    nonrenewable_energy=35000
)

print(result)