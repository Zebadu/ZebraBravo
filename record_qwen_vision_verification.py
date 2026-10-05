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
    "Canonical Zoey image loaded successfully as a local RGB image.",
    "Image dimensions were 1360 x 1440 pixels.",
    "Qwen3-VL generated a detailed visual description from the image.",
    "Description correctly identified major observable facial, hair, eye, skin, expression, pose, background, and lighting characteristics.",
    "Qwen3-VL image understanding test completed successfully."
]

if not service.verify(
    entry_id,
    evidence,
    "test_qwen_vision.py"
):
    raise SystemExit("QWEN KNOWLEDGE RECORD NOT FOUND — NO CHANGE CONFIRMED")

entry = service.get_by_id(entry_id)

entry["metadata"]["inference_verified"] = True
entry["metadata"]["image_understanding_verified"] = True
entry["metadata"]["vision_test_image"] = "AA Revised Cannonical .png"

repository.save(service.get_all())

print("QWEN VISION KNOWLEDGE: VERIFIED")
print("Status:", entry["status"])
print("Inference verified:", entry["metadata"]["inference_verified"])
print("Image understanding verified:", entry["metadata"]["image_understanding_verified"])
print("Vision test image:", entry["metadata"]["vision_test_image"])
print("Evidence count:", len(entry["evidence"]))
