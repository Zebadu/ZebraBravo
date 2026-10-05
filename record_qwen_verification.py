from pathlib import Path
import sys

PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT / "modules"))

from json_environment_knowledge_repository import JsonEnvironmentKnowledgeRepository
from environment_knowledge_service import EnvironmentKnowledgeService

knowledge_file = PROJECT_ROOT / "data" / "environment_knowledge.json"

repository = JsonEnvironmentKnowledgeRepository(knowledge_file)
service = EnvironmentKnowledgeService(repository)

entry_id = "qwen3-vl-4b-instruct"

evidence = [
    "Qwen3-VL-4B-Instruct loaded successfully from the local model directory.",
    "Both checkpoint shards loaded successfully.",
    "Model class reported as Qwen3VLForConditionalGeneration.",
    "Model device map reported GPU device 0.",
    "AutoProcessor loaded successfully.",
    "4-bit NF4 quantization loaded successfully on the RTX 2060.",
    "CUDA was available during the successful model load test.",
    "Image understanding has not yet been tested."
]

result = service.verify(
    entry_id,
    evidence,
    "test_qwen_load.py"
)

if not result:
    raise SystemExit("QWEN KNOWLEDGE RECORD NOT FOUND — NO CHANGE CONFIRMED")

entry = service.get_by_id(entry_id)

if entry["status"] != "verified":
    raise SystemExit("QWEN KNOWLEDGE RECORD WAS NOT PROMOTED TO VERIFIED")

entry["metadata"]["inference_verified"] = True
entry["metadata"]["image_understanding_verified"] = False
entry["metadata"]["model_class"] = "Qwen3VLForConditionalGeneration"
entry["metadata"]["device_map"] = {"": 0}
entry["metadata"]["quantization"] = "4-bit NF4"

repository.save(service.get_all())

print("QWEN KNOWLEDGE RECORD: VERIFIED")
print("Status:", entry["status"])
print("Inference verified:", entry["metadata"]["inference_verified"])
print("Image understanding verified:", entry["metadata"]["image_understanding_verified"])
print("Evidence count:", len(entry["evidence"]))
