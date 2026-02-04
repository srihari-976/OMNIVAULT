#!/bin/bash

echo "======================================"
echo " WSL GPU Setup for Llama RAG Backend"
echo "======================================"

echo ""
echo "Checking CUDA installation..."

# Check if nvidia-smi is available
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA driver detected!"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
    echo ""
else
    echo "❌ nvidia-smi not found!"
    echo ""
    echo "Please ensure:"
    echo "1. You have an NVIDIA GPU"
    echo "2. NVIDIA drivers are installed on Windows"
    echo "3. WSL 2 is being used (not WSL 1)"
    echo "4. WSL CUDA drivers are installed"
    echo ""
    echo "Installation guide:"
    echo "https://docs.nvidia.com/cuda/wsl-user-guide/index.html"
    exit 1
fi

# Check CUDA toolkit
echo "Checking CUDA toolkit..."
if command -v nvcc &> /dev/null; then
    echo "✓ CUDA toolkit installed!"
    nvcc --version
else
    echo "⚠ CUDA toolkit not found"
    echo "Installing CUDA toolkit..."
    
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y cuda-toolkit-12-1
    else
        echo "Please install CUDA toolkit manually for your distribution"
    fi
fi

echo ""
echo "Testing PyTorch CUDA availability..."

# Create a test Python script
cat > /tmp/test_cuda.py << 'EOF'
import sys
try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"GPU Count: {torch.cuda.device_count()}")
        print("\n✓ GPU is ready for use!")
    else:
        print("\n❌ CUDA not available in PyTorch")
        print("You may need to reinstall PyTorch with CUDA support:")
        print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    sys.exit(0 if torch.cuda.is_available() else 1)
except ImportError:
    print("PyTorch not installed yet")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)
EOF

python3 /tmp/test_cuda.py
TEST_RESULT=$?

rm /tmp/test_cuda.py

echo ""
echo "======================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo " GPU Setup: SUCCESS ✓"
    echo "======================================"
    echo ""
    echo "Your system is ready to run Llama with GPU acceleration!"
else
    echo " GPU Setup: NEEDS ATTENTION"
    echo "======================================"
    echo ""
    echo "Please install CUDA-enabled PyTorch:"
    echo "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
fi

echo ""
