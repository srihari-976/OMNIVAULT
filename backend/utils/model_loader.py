"""
Model Loader Module
Handles Llama model initialization, GPU detection, and model management
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import psutil
from config import Config

class ModelManager:
    _instance = None
    _model = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            print("Initializing ModelManager...")
            self.device = self._get_device()
            self.gpu_info = self._get_gpu_info()
    
    def _get_device(self):
        """Detect available device (CUDA or CPU)"""
        if torch.cuda.is_available():
            print(f"✓ CUDA is available!")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA Version: {torch.version.cuda}")
            return "cuda"
        else:
            print("⚠ CUDA not available, using CPU")
            return "cpu"
    
    def _get_gpu_info(self):
        """Get GPU information"""
        if self.device == "cuda":
            return {
                "available": True,
                "name": torch.cuda.get_device_name(0),
                "memory_total": torch.cuda.get_device_properties(0).total_memory / 1e9,
                "cuda_version": torch.version.cuda
            }
        return {
            "available": False,
            "name": "CPU",
            "memory_total": psutil.virtual_memory().total / 1e9,
            "cuda_version": None
        }
    
    def load_model(self):
        """Load Llama model with 4-bit quantization"""
        if self._model is not None:
            print("Model already loaded!")
            return self._model, self._tokenizer
        
        print(f"\n{'='*60}")
        print(f"Loading Llama Model: {Config.MODEL_NAME}")
        print(f"{'='*60}")
        
        try:
            # Load tokenizer
            print("Loading tokenizer...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                Config.MODEL_NAME,
                token=Config.HUGGINGFACE_TOKEN,
                cache_dir=Config.MODEL_CACHE_DIR
            )
            
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # Configure quantization
            quantization_config = None
            if Config.USE_4BIT_QUANTIZATION and self.device == "cuda":
                print("Configuring 4-bit quantization...")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load model
            print("Loading model (this may take a few minutes)...")
            self._model = AutoModelForCausalLM.from_pretrained(
                Config.MODEL_NAME,
                token=Config.HUGGINGFACE_TOKEN,
                quantization_config=quantization_config,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                cache_dir=Config.MODEL_CACHE_DIR,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self._model = self._model.to(self.device)
            
            print(f"\n✓ Model loaded successfully!")
            print(f"  Device: {self.device.upper()}")
            if self.device == "cuda":
                print(f"  Quantization: 4-bit")
                print(f"  Memory allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
            print(f"{'='*60}\n")
            
            return self._model, self._tokenizer
            
        except Exception as e:
            print(f"\n✗ Error loading model: {str(e)}")
            raise
    
    def generate(self, prompt, max_new_tokens=None, temperature=None, top_p=None, top_k=None):
        """Generate text using the loaded model"""
        if self._model is None or self._tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Use config defaults if not specified
        max_new_tokens = max_new_tokens or Config.MAX_NEW_TOKENS
        temperature = temperature or Config.TEMPERATURE
        top_p = top_p or Config.TOP_P
        top_k = top_k or Config.TOP_K
        
        # Tokenize input
        inputs = self._tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=2048)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=Config.REPETITION_PENALTY,
                do_sample=True,
                pad_token_id=self._tokenizer.pad_token_id,
                eos_token_id=self._tokenizer.eos_token_id
            )
        
        # Decode output
        generated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the input prompt from the output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
    
    def get_status(self):
        """Get model status"""
        return {
            "loaded": self._model is not None,
            "device": self.device,
            "gpu_info": self.gpu_info,
            "model_name": Config.MODEL_NAME if self._model is not None else None
        }


def load_llama_model():
    """Convenience function to load model"""
    manager = ModelManager()
    return manager.load_model()


def get_gpu_info():
    """Convenience function to get GPU info"""
    manager = ModelManager()
    return manager.gpu_info


if __name__ == "__main__":
    # Test model loading
    print("Testing model loading...\n")
    model, tokenizer = load_llama_model()
    
    # Test generation
    print("\nTesting generation...")
    manager = ModelManager()
    response = manager.generate("Hello, how are you?", max_new_tokens=50)
    print(f"Response: {response}")
