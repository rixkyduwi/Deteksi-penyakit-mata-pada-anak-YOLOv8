import torch

# Load the model
model_path = "best.pt"
model = torch.load(model_path)

# Check the model's attributes to determine the version
model_info = {
    "class_name": model.__class__.__name__,
    "model_details": model
}

model_info
print(model_info)