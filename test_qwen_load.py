from pathlib import Path

from transformers import AutoProcessor, AutoModelForVision2Seq, BitsAndBytesConfig
import torch

MODEL = Path(r"C:\Users\qst4t\Documents\ComfyUI\models\LLM\Qwen-VL\Qwen3-VL-4B-Instruct")

print("QWEN LOAD TEST")
print("Model:", MODEL)
print("CUDA:", torch.cuda.is_available())
print("VRAM:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2), "GB")

quantization = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
)

print("Loading Qwen3-VL-4B-Instruct in 4-bit...")

model = AutoModelForVision2Seq.from_pretrained(
    MODEL,
    quantization_config=quantization,
    device_map="auto",
    trust_remote_code=True,
).eval()

print("QWEN MODEL LOAD: PASS")
print("Model class:", type(model).__name__)
print("Device map:", getattr(model, "hf_device_map", "not reported"))

processor = AutoProcessor.from_pretrained(
    MODEL,
    trust_remote_code=True,
)

print("QWEN PROCESSOR LOAD: PASS")
print("QWEN PROOF-OF-LIFE: PASS")
