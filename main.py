# main.py - SLM Inference Server
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import tiktoken
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.8
    top_k: int = 40

try:
    enc = tiktoken.get_encoding("gpt2")
    print("Tokenizer loaded successfully.")
except Exception as e:
    print(f"Warning: tiktoken not found. Error: {e}")
    enc = None

@app.get("/")
async def root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(current_dir, "index.html"))

@app.get("/health")
async def health_check():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path   = os.path.join(current_dir, "inference")
    model_path = os.path.join(current_dir, "model.bin")
    return {
        "status": "ok",
        "inference_exe_found": os.path.exists(exe_path),
        "model_bin_found":     os.path.exists(model_path),
        "working_directory":   current_dir
    }

@app.post("/generate")
async def generate_text(req: GenerateRequest):
    if enc is None:
        raise HTTPException(status_code=500, detail="Tokenizer not loaded.")

    input_tokens = enc.encode(req.prompt)
    token_str    = ",".join(map(str, input_tokens))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path    = os.path.join(current_dir, "inference")
    model_path  = os.path.join(current_dir, "model.bin")

    if not os.path.exists(exe_path):
        raise HTTPException(status_code=500, detail=f"inference binary not found: {exe_path}")

    if not os.path.exists(model_path):
        raise HTTPException(status_code=500, detail=f"model.bin not found: {model_path}")

    try:
        start_time = time.perf_counter()
        # --------------------------------------------------------
        # Subprocess IPC Boundary:
        # We pass the prompt tokens as a comma-separated string argument.
        # The C++ binary executes completely isolated from the Python GIL.
        # --------------------------------------------------------
        process = subprocess.run(
            [exe_path, token_str, str(req.max_tokens), str(req.temperature), str(req.top_k)],
            capture_output=True,
            text=True,
            cwd=current_dir
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    if process.returncode != 0 and not process.stdout.strip():
        stdout_msg = process.stdout.strip() if process.stdout else ""
        stderr_msg = process.stderr.strip() if process.stderr else ""
        raise HTTPException(status_code=500, detail=f"C++ Error | stdout: '{stdout_msg}' | stderr: '{stderr_msg}'")

    try:
        output_str = process.stdout.strip()
        generated_ids = []
        if output_str:
            # Parse space-separated token IDs printed to stdout by C++
            for x in output_str.split():
                try:
                    generated_ids.append(int(x))
                except ValueError:
                    pass

        generated_text = enc.decode(generated_ids) if generated_ids else ""
        tokens_out     = len(generated_ids)
        tokens_per_sec = round(tokens_out / (elapsed_ms / 1000), 2) if elapsed_ms > 0 else 0

        return {
            "prompt":         req.prompt,
            "generated_text": generated_text,
            "tokens_in":      len(input_tokens),
            "tokens_out":     tokens_out,
            "latency_ms":     round(elapsed_ms, 2),
            "tokens_per_sec": tokens_per_sec
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding error: {str(e)}")
