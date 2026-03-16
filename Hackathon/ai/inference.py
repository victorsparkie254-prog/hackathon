import onnxruntime as ort
import numpy as np
from PIL import Image
import json
import os

# Define the disease classes
CLASSES = ['Healthy', 'Northern Leaf Blight', 'Common Rust', 'Gray Leaf Spot']

def preprocess_image(image_path):
    """
    Preprocess the image for EfficientNet-B0 ONNX model.
    Resizes, normalizes, and converts format to CHW.
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    
    # Convert to numpy and normalize (ImageNet stats)
    img_data = np.array(img).astype('float32') / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img_data = (img_data - mean) / std
    
    # HWC to CHW
    img_data = np.transpose(img_data, (2, 0, 1))
    
    # Add batch dimension
    img_data = np.expand_dims(img_data, axis=0)
    return img_data

def predict(image_path, model_path="models/crop_disease_model.onnx"):
    print(f"Loading ONNX model from {model_path}...")
    if not os.path.exists(model_path):
        return {"error": "Model not found. Please run train.py first to generate the ONNX model."}
        
    try:
        session = ort.InferenceSession(model_path)
    except Exception as e:
        return {"error": f"Error loading model: {str(e)}"}
        
    input_name = session.get_inputs()[0].name
    
    print(f"Preprocessing image: {image_path}")
    input_data = preprocess_image(image_path)
    
    print("Running inference on CPU...")
    result = session.run(None, {input_name: input_data})
    
    # Apply softmax to get confidence scores
    logits = result[0][0]
    exp_logits = np.exp(logits - np.max(logits))
    probabilities = exp_logits / exp_logits.sum()
    
    pred_class_idx = np.argmax(probabilities)
    confidence = probabilities[pred_class_idx]
    
    return {
        "prediction": CLASSES[pred_class_idx],
        "confidence": float(confidence)
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        result = predict(img_path)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python inference.py <path_to_image>")
