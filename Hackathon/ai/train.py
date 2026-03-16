import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import os

# Define the target crop disease classes
CLASSES = ['Healthy', 'Northern Leaf Blight', 'Common Rust', 'Gray Leaf Spot']
NUM_CLASSES = len(CLASSES)
BATCH_SIZE = 32
NUM_EPOCHS = 5

def create_model():
    print("Initializing EfficientNet-B0 for transfer learning...")
    
    # Load pretrained EfficientNet-B0
    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    
    # Freeze the base layers for feature extraction
    for param in model.parameters():
        param.requires_grad = False
        
    # Replace the final classification head
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    
    return model

def export_to_onnx(model, onnx_path="models/crop_disease_model.onnx"):
    print(f"Exporting the model to ONNX format at {onnx_path}...")
    
    # Set model to evaluation mode
    model.eval()
    
    # Create a dummy input tensor corresponding to the expected input shape
    # Batch Size: 1, Channels: 3, Height: 224, Width: 224
    dummy_input = torch.randn(1, 3, 224, 224)
    
    os.makedirs(os.path.dirname(onnx_path), exist_ok=True)
    
    # Export the model
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print("ONNX export completed successfully.")

def train():
    model = create_model()
    
    # Setup loss function and optimizer (only training the new head)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
    
    print(f"Simulating training for {NUM_EPOCHS} epochs on a generic crop dataset...")
    # NOTE: In a real-world scenario, you would use torchvision.datasets.ImageFolder 
    # to load a dataset like PlantVillage, alongside a DataLoader for batching.
    
    # for epoch in range(NUM_EPOCHS):
    #     # training loop logic
    #     pass
    
    print("Mock training complete.")
    
    # Save the standard PyTorch weights
    os.makedirs("models", exist_ok=True)
    torch_path = "models/crop_disease_efficientnet.pth"
    torch.save(model.state_dict(), torch_path)
    print(f"PyTorch model weights saved to {torch_path}")
    
    # Export to ONNX for mobile/edge inference
    export_to_onnx(model)

if __name__ == "__main__":
    train()
