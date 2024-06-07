import torch
import torchvision
from torch import nn
from torchvision import transforms
from PIL import Image
import os
import numpy as np
import torch.nn.functional as F
import time


# configuration class
class CFG:
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'   # cuda if a GPU is available
    NUM_DEVICES = torch.cuda.device_count()  # number of available GPU devices
    NUM_WORKERS = os.cpu_count() # number of available CPUs
    NUM_CLASSES = 5  # number of classification classes (clean vs. dirty vs. Bird_drop vs.Electrical_damage vs.physical_damage)
    EPOCHS = 10    # number of iterations of the training phase
    BATCH_SIZE = (
        32 if torch.cuda.device_count() < 2
        else (32 * torch.cuda.device_count())
    )
    LR = 0.001  # learning rate
    APPLY_SHUFFLE = True
    SEED = 2024
    HEIGHT = 256  # height of an input image
    WIDTH = 256   # width of an input image
    CHANNELS = 3  # 3 channels (RGB)
    IMAGE_SIZE = (256, 256, 3)


def build_model(device: torch.device=CFG.NUM_CLASSES) -> nn.Module:
    # Set the manual seeds
    torch.manual_seed(CFG.SEED)
    torch.cuda.manual_seed(CFG.SEED)

    # Get model weights
    model_weights = (
        torchvision
        .models
        .EfficientNet_V2_L_Weights
        .DEFAULT
    )

    # Get model and push to device
    model = (
        torchvision.models.efficientnet_v2_l(
            weights=model_weights
        )
    ).to(device)

    # Freeze Model Parameters
    for param in model.features.parameters():
        param.requires_grad = False  # the weights of the feature extractor will not be updated during the training process.

    # Define new classifier and push to the target device
    # only the weights of the newly added classifier (the fully connected layer with dropout) will be updated during training.
    model.classifier = nn.Sequential(
        nn.Flatten(),
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(
            in_features=1280, out_features=CFG.NUM_CLASSES,bias=True
        )
    ).to(device)

    return model


   # Load the efficientNetV2 model
def load_model():
 
    # Step 1: Build the model 
    model = build_model(device=CFG.DEVICE)

    # Step 2: Load the weights into the model
    model.load_state_dict(torch.load('my_efficientnetv2_model.pth',map_location='cpu'))

    # Step 3: Set the model to evaluation mode
    model.eval()

    return model


# classifyig the input image
def classify_image(input_image_path,model):

    start_time = time.time()
   
    # Load the image
    image = Image.open(input_image_path)

  # input transforms:
    transform = transforms.Compose([
        transforms.Resize((CFG.HEIGHT, CFG.WIDTH)),  # Reshape to be consistent with the hyperparameters of the configuration class
        transforms.ToTensor(),  # Converts the image to a PyTorch tensor
    ])

    # apply input transforms
    image = transform(image)
    image = image.unsqueeze(0) # Add a batch dimension


    # Make a prediction
    with torch.no_grad():
        prediction= model(image)
    
    total_time = time.time() - start_time

    # Apply softmax to get probabilities
    prediction_probs = F.softmax(prediction, dim=1)
    
    total_time = time.time() - start_time

    # Convert the prediction to a NumPy array
    prediction_probs = prediction_probs.cpu().numpy()

    #print(prediction_probs)

    # Using NumPy's argmax to find the predicted class index
    result = np.argmax(prediction_probs, axis=1)

    # Define mapping 
    class_labels = {0: 'bird_drop', 1: 'clean', 2: 'dirty', 3: 'Electrical_damage', 4: 'physical_damage'}
    predicted_label = class_labels[result.item()]
    predicted_prob = prediction_probs[0][result.item()]  # Extract probability of the predicted label
    formatted_prob = "{:.2f}%".format(predicted_prob * 100)

   # print(f"The predicted label is: {predicted_label}")
   # print(f"The probability of the predicted label is: {formatted_prob}")
  

    return predicted_label, formatted_prob