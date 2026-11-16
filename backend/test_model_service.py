from model_service import model_service


input_data = {
    "total_energy": 50000,
    "renewable_energy": 15000,
    "nonrenewable_energy": 35000,
    "production_output": 10000,
    "transport_distance": 1500,
    "raw_material_usage": 5000,
    "employment_count": 100
}


print("\n" + "=" * 60)
print("CARBON AI - MODEL SERVICE TEST")
print("=" * 60)


result = model_service.predict(
    input_data
)

print("\nPrediction result:")

for key, value in result.items():

    print(
        f"{key}: {value}"
    )


print("\n" + "=" * 60)
print("MODEL INFORMATION")
print("=" * 60)

info = model_service.get_model_info()

print(
    "Model loaded:",
    info["model_loaded"]
)

print(
    "Model type:",
    info["model_type"]
)

print(
    "\nFeatures:"
)

for feature in info["features"]:

    print(
        " -",
        feature
    )


print("\nFeature importance:")

for item in model_service.get_feature_importance():

    print(
        f" - {item['feature']}: "
        f"{item['importance']}"
    )