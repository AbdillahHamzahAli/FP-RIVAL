import torch
import torch.version

# Get CUDA version
cuda_version = torch.version.cuda if torch.cuda.is_available() else "CUDA not available"

# Get PyTorch version
pytorch_version = torch.__version__

print(f"CUDA version: {cuda_version}")
print(f"PyTorch version: {pytorch_version}")
