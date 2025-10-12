#!/usr/bin/env python3
"""
PyTorch CUDA Functionality Test Script
"""

import sys
import torch

def test_pytorch_cuda():
    """Test PyTorch CUDA functionality"""
    print("=" * 60)
    print("           PyTorch CUDA Functionality Test")
    print("=" * 60)

    print(f"Python Version: {sys.version}")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"PyTorch Installation Path: {torch.__file__}")
    print()

    # Check CUDA compilation version
    cuda_version = torch.version.cuda
    print(f"CUDA Compilation Version: {cuda_version}")

    # Check CUDA runtime availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Runtime Available: {cuda_available}")

    if cuda_available:
        print(f"CUDA Device Count: {torch.cuda.device_count()}")
        print(f"Current Device: {torch.cuda.current_device()}")
        print(f"Device Name: {torch.cuda.get_device_name(0)}")

        # Get GPU properties
        device_props = torch.cuda.get_device_properties(0)
        print(f"Total GPU Memory: {device_props.total_memory / 1024**3:.1f} GB")
        print(f"Compute Capability: {device_props.major}.{device_props.minor}")

        # Simple GPU computation test
        print("\nRunning simple GPU computation test...")
        try:
            # Create tensors and move to GPU
            x = torch.randn(1000, 1000)
            y = torch.randn(1000, 1000)

            print(f"CPU tensor created successfully: x.shape = {x.shape}")

            # Move to GPU
            x_gpu = x.to('cuda')
            y_gpu = y.to('cuda')

            print(f"GPU tensor moved successfully: x_gpu.device = {x_gpu.device}")

            # GPU computation
            z_gpu = torch.mm(x_gpu, y_gpu)

            print(f"GPU matrix multiplication successful: z_gpu.shape = {z_gpu.shape}")
            print("CUDA functionality is fully working!")

        except Exception as e:
            print(f"GPU computation test failed: {e}")
    else:
        print("CUDA not available")
        print("\nPossible reasons:")
        print("1. CPU version of PyTorch installed")
        print("2. Incompatible NVIDIA driver")
        print("3. CUDA runtime not installed")
        print("4. System environment variable issues")

    print("=" * 60)

if __name__ == "__main__":
    test_pytorch_cuda()