from huggingface_hub import HfApi

# Initialize the API (will use the token from CLI authentication)
api = HfApi()

# Define your repository ID
repo_id = "AshutoshAI/mental-health-predictor"

# Upload the entire folder, excluding unnecessary files
api.upload_folder(
    folder_path="D:/DSMINIPRO",
    repo_id=repo_id,
    repo_type="model",
    ignore_patterns=["*.csv", "*le_gender.pkl", "*le_target.pkl", "*mental_health_model.pkl", "*scaler.pkl", "*scaler_updated.pkl", "*.log"],
)
print(f"Successfully uploaded to {repo_id}")