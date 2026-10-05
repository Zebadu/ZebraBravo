from pathlib import Path
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq, BitsAndBytesConfig

MODEL = Path(r"C:\Users\qst4t\Documents\ComfyUI\models\LLM\Qwen-VL\Qwen3-VL-4B-Instruct")
IMAGE = Path(r"C:\Users\qst4t\Documents\ComfyUI\input\AA Revised Cannonical .png")

print("QWEN VISION TEST")
print("Image:", IMAGE)
print("Image exists:", IMAGE.exists())

image = Image.open(IMAGE).convert("RGB")
print("Image size:", image.size)

quantization = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
)

print("Loading Qwen3-VL-4B-Instruct...")
model = AutoModelForVision2Seq.from_pretrained(
    MODEL,
    quantization_config=quantization,
    device_map="auto",
    trust_remote_code=True,
).eval()

processor = AutoProcessor.from_pretrained(
    MODEL,
    trust_remote_code=True,
)

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {
                "type": "text",
                "text": "Describe this image in detail. Identify the person, their visible physical characteristics, clothing, pose, expression, background, lighting, and overall visual style. Only describe what you can actually observe."
            },
        ],
    }
]

prompt = processor.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = processor(
    text=[prompt],
    images=[image],
    return_tensors="pt",
)

inputs = {
    key: value.to(model.device) if hasattr(value, "to") else value
    for key, value in inputs.items()
}

print("Generating visual description...")

with torch.inference_mode():
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=512,
    )

input_length = inputs["input_ids"].shape[1]
generated_ids = generated_ids[:, input_length:]

answer = processor.batch_decode(
    generated_ids,
    skip_special_tokens=True,
    clean_up_tokenization_spaces=False,
)[0]

print()
print("=" * 70)
print("QWEN VISUAL DESCRIPTION")
print("=" * 70)
print(answer)
print("=" * 70)
print("QWEN IMAGE UNDERSTANDING TEST: PASS")
