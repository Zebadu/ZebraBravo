# ZEBRABRAVO / ZOEY ? BOOT PACKET
## Project Continuity Record ? 2026-10-03

> Purpose: prevent repeated architectural archaeology. This document records the established ZebraBravo state, verified capabilities, important boundaries, and current engineering position.

## Identity & Authority

- User: Zeb Hall.
- Assistant identity in this project: Zoey.
- ZebraBravo is Zeb's project.
- Zeb is owner/architect and highest authority.
- Zoey is the reasoning, intelligence, orchestration and systems/architecture partner.
- ZWMD = challenge assumptions, reason independently, use execution discretion within governance.
- FULL THROTTLE = proceed as far as available tools and governance safely permit.

## Core Principle

> Don't use more capability than the task requires. Concentrate capability exactly where needed, under control, and verify the result.

This is the project's "laser welding" principle.

## Existing Architecture

ZebraBravo already contains:

- Truth Gate
- Policy Gate
- Capability Fabric
- Capability Registry / Runtime
- Continuity
- Artifact Registry
- Visual Gateway
- PowerShell X-Ray
- PowerShell execution capability
- Windows diagnostics
- Development Interface
- Development Protocol
- Development Transport
- Development Service
- Development Bridge
- Development Authorization
- governed filesystem write capability
- governed test capability
- Git capability
- Zoey identity capability

Do not propose parallel infrastructure without first inspecting the existing architecture.

## Development Bridge

The existing Development Bridge is a local HTTP interface.

Verified configuration:

- host: 127.0.0.1
- port: 52336
- authentication: Bearer token from `ZEBRABRAVO_DEVELOPMENT_TOKEN`
- `/health` is unauthenticated
- `/development` is authenticated
- arbitrary Python execution is not provided
- requests route through the existing Development Service

Important distinction:

**Bridge token != Development Mode.**

The token authenticates access to the local bridge.

Development Authorization controls whether development operations such as governed writes/tests are permitted.

The Policy Gate remains authoritative.

The token must never be recorded in this document or pasted into chat.

## Verified Development Bridge Results

ZebraBravo successfully:

1. Started through `core/main.py`.
2. Responded successfully to `/health`.
3. Confirmed the development token exists locally without exposing it.
4. Read Development Mode through the authenticated bridge.
5. Activated Development Mode through the authenticated bridge.

Verified flow:

AUTHENTICATE
? Development Bridge
? Development Protocol
? Development Service
? Development Authorization

Development Mode was successfully changed from `False` to `True` through the authenticated bridge.

## Development Request Flow

External/local client
? Development Bridge
? Development Service
? Development Transport
? Development Protocol
? Development Interface
? Capability Runtime
? Policy Gateway
? Capability Executor
? Capability

For governed write/test operations, Development Authorization and the appropriate permissions are required.

## Self-Inspection

ZebraBravo can inspect itself.

The existing `DevelopmentInterface` exposes:

- project_info
- list
- read
- write
- search
- git_status
- git_log
- git_diff
- powershell_xray
- desktop
- powershell_execute
- windows_diagnostics
- test

A direct `project_info` inspection was successfully executed on 2026-10-03.

The returned runtime reported these registered capabilities:

- archive
- continuity
- desktop
- filesystem
- filesystem_write
- git
- powershell_execute
- powershell_xray
- test
- truth
- visual
- windows_diagnostics
- zoey_identity

The same inspection reported the actual workspace and current Git state.

## Current Git Baseline ? 2026-10-03

HEAD and origin/main were both:

`3a5eeaa Add governed live terminal observation`

Working-tree changes intentionally present at inspection time:

- `modules/intent/simple_reasoner.py`
- `tests/test_local_intelligence.py`
- `tests/test_runtime_governance_context.py`
- `comfyui.prev.log`
- `comfyui.prev2.log`
- `data/_archive_2026-09-30/`

These items are NOT part of this documentation change and must not be swept into the documentation commit.

## ?????? EYES ? Verified Milestone

ZebraBravo has a governed desktop capture pathway.

The Desktop Gateway uses the Windows desktop and returns actual captured pixel data.

A real Windows PowerShell capture was verified with:

- dimensions: 1129 x 958
- format: BGRA
- image payload: 4,326,328 bytes

The governed `DesktopCapability` successfully converted the capture into:

`VisualObservation`

with:

- source: desktop
- provenance: local_desktop_capture
- actual pixel payload
- dimensions: 1129 x 958
- format: BGRA

Therefore:

**PROVEN: ZebraBravo's governed ?????? EYES can acquire actual Windows pixels and return them as a VisualObservation.**

## Qwen-VL ? Verified Infrastructure

The ComfyUI ecosystem already contains genuine Qwen3-VL implementation code, including:

- `comfy/text_encoders/qwen3vl.py`
- `comfy/text_encoders/qwen_vl.py`
- Qwen3-VL model/config support
- Qwen-VL processing of actual image tensors

The Qwen-VL custom node already exists in Documents ComfyUI:

`custom_nodes/ComfyUI-QwenVL`

It supports Qwen3-VL and Qwen2.5-VL multimodal image/video reasoning.

## Local Qwen Models

The Documents ComfyUI installation already contains local Hugging Face-style Qwen3-VL models:

- `models/LLM/Qwen-VL/Qwen3-VL-2B-Instruct`
- `models/LLM/Qwen-VL/Qwen3-VL-4B-Instruct`

The Qwen3-VL 2B model contains a complete local model payload including:

- `model.safetensors` (~4.06 GB)
- tokenizer files
- configuration
- preprocessing configuration
- generation configuration

Qwen2.5-VL 7B weights are also present separately in:

`models/text_encoders`

including approximately 15.45 GB and 8.74 GB variants.

Important:

The ComfyUI-QwenVL custom node expects Hugging Face-style model directories under the Qwen-VL model path. Do not assume the standalone text-encoder weights are interchangeable with those model directories.

## GPU / Runtime Evidence

Verified environment:

- GPU: NVIDIA GeForce RTX 2060
- VRAM: 6144 MB
- Torch: 2.10.0+cu130
- CUDA available: True
- Transformers: 4.57.6
- BitsAndBytes: 0.49.2

Qwen3-VL model configuration indicates approximately:

- 2B: 4 GB full precision-class VRAM requirement, lower with quantization
- 4B: 6 GB full precision-class VRAM requirement, lower with quantization

For the first controlled visual reasoning test, Qwen3-VL-2B-Instruct is the intended diagnostic model.

## Critical Architectural Boundary

The architecture must preserve this distinction:

**?????? EYES acquire reality.**

**Qwen-VL is a visual reasoning engine that interprets what the EYES acquire.**

Qwen must not be treated as the EYES themselves.

The intended conceptual path is:

?????? EYES
? actual pixels
? VisualObservation
? visual reasoning engine such as Qwen3-VL
? interpretation

This preserves separation between observation and interpretation.

## What Is Proven

As of 2026-10-03:

- ZebraBravo starts successfully.
- The Development Bridge is real and running.
- Bridge authentication works.
- Development Authorization can be activated through the bridge.
- ZebraBravo can inspect its own runtime.
- Capability inventory is available.
- Governed desktop capture works.
- Actual Windows pixels can become a VisualObservation.
- Qwen3-VL implementation code exists locally.
- ComfyUI-QwenVL exists locally.
- Local Qwen3-VL 2B and 4B model directories exist.
- The RTX 2060/CUDA/Transformers/BitsAndBytes environment is available.

## What Is NOT Yet Proven

Do not claim these have already been demonstrated:

- arbitrary governed file modification through the authenticated bridge
- complete end-to-end governed code modification
- automated test/fix/verify development cycle
- complete Development Bridge lifecycle
- external Flutter client integration
- automatic provenance/continuity recording for every development action
- fully autonomous development
- actual end-to-end EYES ? VisualObservation ? Qwen3-VL visual reasoning

## Immediate Engineering Target

The next visual milestone is deliberately small:

**one known image**

? **Qwen3-VL-2B-Instruct**

? **"Describe this image in detail."**

Only after that path is verified should the EYES-to-Qwen integration be expanded.

Separately, the next Development Bridge milestone is:

AUTHENTICATE
? AUTHORIZE
? GOVERN
? EXECUTE
? VERIFY
? RECORD

using the smallest harmless governed write.

## Working Method

1. Observe existing architecture.
2. Identify what is already real.
3. Separate VERIFIED from POSSIBLE.
4. Reuse existing capabilities.
5. Make the smallest useful change.
6. Pass through Truth/Policy/Capability governance.
7. Execute.
8. Verify.
9. Record useful provenance/continuity/lessons.
10. Only then proceed.

Zeb should not have to repeatedly remember the architecture in order to continue the project.

This document exists to prevent that repetition.

---

**ZWMD ? WE BUILD THE DOORWAY, NOT THE MAZE.**
