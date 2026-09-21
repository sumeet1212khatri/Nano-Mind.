# Nano-Mind

Zero-dependency GPT-2-style transformer inference engine in C++17 with AVX2/FMA SIMD and OpenMP CPU acceleration.

**Live Demo** | **[Hugging Face Spaces](https://huggingface.co/spaces/NOT-OMEGA/NanoMind)** | **[Live Site](https://nanomind.qd.je/)**

---

## HLD


<img width="1628" height="728" alt="image" src="https://github.com/user-attachments/assets/2dbff255-b45a-4d92-88a6-4d742ce03391" />

<img width="1192" height="820" alt="image" src="https://github.com/user-attachments/assets/4e61e80a-0a3a-4044-a01d-488e96c2e6e5" />
<img width="1167" height="302" alt="image" src="https://github.com/user-attachments/assets/27c49954-0e0a-4a74-88f0-8e923e246fdc" />




## Highlights

- **From-Scratch Implementation**: Complete GPT-2-style transformer inference implemented natively in C++17 without deep learning frameworks.
- **Full Transformer Stack**: Features multi-head self-attention, layer normalization, GELU activation, and top-k stochastic sampling.
- **KV-Cache Optimization**: Implements key-value caching for efficient autoregressive generation, avoiding O(n²) attention recomputation.
- **CPU Acceleration**: Matrix-vector operations accelerated natively using x86 AVX2 256-bit SIMD intrinsics with FMA (Fused Multiply-Add).
- **Parallelism**: Multi-head attention loops and layer operations are parallelized across CPU cores using OpenMP.
- **Zero-Copy Loading**: Custom binary model format (`.bin`) that uses pointer arithmetic to map weights into memory without `memcpy` duplication.
- **FastAPI Backend**: Python REST API layer that bridges `tiktoken` BPE tokenization with the compiled C++ binary via subprocess IPC.
- **Containerized**: Fully containerized setup via Docker with automated build-time C++ compilation and HuggingFace weight retrieval.

---

## Architecture

```text
Browser Client
      │
      ▼ (HTTP POST /generate)
 FastAPI Server (Python)
      │
      ├──> tiktoken: Encodes prompt string to GPT-2 Token IDs
      │
      ▼ (Subprocess IPC: passes Token IDs as CLI args)
 C++ Inference Engine (Compiled Binary)
      │
      ├──> Loads custom model.bin (Zero-copy mapping)
      ├──> Transformer Forward Pass (Embeddings → Blocks → Logits)
      ├──> Hardware Accel: AVX2 / FMA + OpenMP Threads
      └──> Autoregressive Loop: Top-K Sampling + KV-Cache
      │
      ▼ (stdout: Space-separated Token IDs)
 FastAPI Server (Python)
      │
      ├──> tiktoken: Decodes Token IDs back to text string
      │
      ▼ (JSON Response: {text, latency, tokens_per_sec})
Browser Client
```

- **Browser UI**: A vanilla HTML/JS frontend providing a typewriter effect and live performance metrics.
- **FastAPI**: Acts as the orchestrator, handling HTTP requests, tokenizing input, measuring end-to-end latency, and formatting JSON responses.
- **tiktoken**: An external Python library used specifically for matching OpenAI's GPT-2 Byte Pair Encoding vocabulary (50,257 tokens).
- **C++ Binary**: The core computational engine. It reads the mapped weights, runs the mathematical forward pass over the transformer architecture, and samples the next token.

---

## C++ Inference Engine

The engine mathematically replicates the GPT-2 architecture in pure C++:

1.  **Configuration**: Reads a 5-integer header defining `n_layer`, `n_head`, `n_embd`, `block_size`, and `vocab_size`.
2.  **Embeddings**: Adds content token embeddings (`wte`) and positional embeddings (`wpe`).
3.  **Transformer Blocks**: Iterates through `n_layer` blocks. Each block performs:
    -   **Attention**: Projects to Q, K, V. Saves K, V into a pre-allocated **KV-cache**. Computes scaled dot-product attention over the sequence (parallelized across heads via OpenMP).
    -   **MLP**: Feedforward network with an exact **GELU** activation implemented via a `tanh` approximation.
    -   **Residuals & Norm**: Adds residual connections and applies Layer Normalization before attention and MLP steps.
4.  **Logits & Sampling**: Applies final LayerNorm, projects to the 50,257 vocabulary space via the language model head, scales by temperature, and performs cumulative probability **Top-K sampling** to select the next token.

---

## Performance

The following benchmarks were obtained from the live Hugging Face Spaces deployment. 

**Deployment Context:** Hugging Face `cpu-basic` Free Tier infrastructure.
**Date:** 2026-09-08

| Metric | Value |
| :--- | :--- |
| **Median End-to-End Throughput** | **49.7 tokens/sec** |
| **Median End-to-End Latency** | **1,594 ms** (for 100 max tokens) |
| **Server-Side Inference Latency** | **824.98 ms** (median) |
| **Success Rate** | **100%** (20/20 measured requests) |

> **Note:** The "End-to-End Throughput" and "End-to-End Latency" include network round-trip, Hugging Face proxy routing, FastAPI overhead, Python tokenization, subprocess creation, and the C++ inference loop. The "Server-Side Inference Latency" measures strictly the isolated execution of the compiled C++ binary on the host machine.

---

## Tech Stack

-   **Inference**: `C++17`
-   **Acceleration**: `AVX2`, `FMA` (x86 Intrinsics), `OpenMP`
-   **API Server**: `Python 3.10+`, `FastAPI`, `Uvicorn`
-   **Tokenization**: `tiktoken`
-   **Frontend**: `HTML`, `CSS`, `JavaScript` (Vanilla)
-   **Deployment**: `Docker`, `Hugging Face Spaces`

---

## Project Structure

| File / Directory | Purpose |
| :--- | :--- |
| `inference.cpp` | Core C++ transformer engine (AVX2 + OpenMP implementation). |
| `main.py` | FastAPI application, subprocess orchestrator, and tiktoken integration. |
| `index.html` | Vanilla frontend UI with live performance metrics and typewriter text rendering. |
| `benchmark.py` | Script to evaluate isolated local API performance. |
| `benchmark_huggingface.py` | Script to evaluate live end-to-end performance against the deployed HF Space. |
| `Dockerfile` | Multi-stage build for compiling C++, downloading weights, and running Uvicorn. |
| `requirements.txt` | Python dependencies. |
| `SETUP_GUIDE.md` | Detailed instructions for local compilation and execution. |

---

## Running Locally

### Prerequisites
- Python 3.10+
- A C++ Compiler supporting C++17, OpenMP, and AVX2 (e.g., GCC/MinGW, Clang).

### 1. Build the C++ Engine
Compile the inference engine with maximum optimizations:
```bash
g++ -O3 -march=native -fopenmp -mavx2 -mfma -std=c++17 inference.cpp -o inference.exe -lm
```
*(On Linux/macOS, use `-o inference` instead of `inference.exe`)*

### 2. Install Python Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Obtain Model Files
Download the custom binary weights (`model.bin`) and tokenizer config (`tokenizer.bin`) and place them in the project root next to the compiled binary.
```bash
curl -L -o model.bin "https://huggingface.co/spaces/NOT-OMEGA/Inference/resolve/main/model.bin"
curl -L -o tokenizer.bin "https://huggingface.co/spaces/NOT-OMEGA/Inference/resolve/main/tokenizer.bin"
```

### 4. Start the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Access the Frontend
Open `http://localhost:8000` in your web browser.

---

## API Documentation

### `POST /generate`
Generates text autoregressively based on the provided prompt.

**Request Body (JSON):**
```json
{
  "prompt": "Explain how a CPU-based transformer inference engine works.",
  "max_tokens": 100,
  "temperature": 0.8,
  "top_k": 40
}
```

**Response (JSON):**
```json
{
  "prompt": "Explain how a CPU-based transformer inference engine works.",
  "generated_text": " A CPU-based transformer inference engine relies on...",
  "tokens_in": 12,
  "tokens_out": 100,
  "latency_ms": 1651.24,
  "tokens_per_sec": 60.56
}
```

### `GET /health`
Returns the status of the server and verifies the existence of required binary/model files.

---

## Benchmarking

Two benchmarking scripts are provided:

1.  **`benchmark.py`**: Tests the *local* API instance running on your machine. Useful for measuring absolute hardware performance without network overhead.
2.  **`benchmark_huggingface.py`**: Tests the *live* Hugging Face Spaces deployment. Simulates end-to-end user experience including network latency and proxy overhead.

Both scripts perform initial warmup runs (discarded from statistics) followed by measured sequential runs, calculating mean/median latencies, per-token latencies, and throughput.

---

## Design Decisions

-   **Why C++ for Inference?** To maintain tight control over memory allocation, pointer arithmetic, and CPU execution without the massive dependency footprint (GBs) of PyTorch/TensorFlow.
-   **Why AVX2/FMA & OpenMP?** Modern CPUs are heavily underutilized by single-threaded scalar code. AVX2 processes 8 floats per instruction cycle, and FMA combines multiplication and addition. OpenMP trivializes threading across independent attention heads and matrix rows.
-   **Why a Custom Binary Format?** Standard formats like ONNX are complex to parse. A raw binary dump of sequential float32 weights allows loading via a single bulk `fread()`, mapping pointers directly into the buffer without `memcpy` overhead (Zero-copy loading).
-   **Why FastAPI + Subprocess?** While C++ bindings (e.g., `pybind11`) offer tighter integration, a subprocess boundary decouples the Python web layer from the C++ computation layer. It makes the C++ binary independently testable and avoids Python Global Interpreter Lock (GIL) concerns, at the cost of minor OS process-creation overhead (~10ms).

---

## Limitations

-   **CPU-Only**: The engine exclusively uses x86 CPU instructions. There is no CUDA, Metal, or general GPU acceleration implemented.
-   **Float32 Precision**: Weights are stored and computed in 32-bit floating-point precision. Int8/Int4 quantization is not currently supported.
-   **Synchronous Generation**: The `/generate` endpoint blocks until the entire sequence is computed and returns the full string at once. Streaming (e.g., Server-Sent Events) is not implemented.
-   **No Production Guardrails**: The API is designed for demonstration. It lacks authentication, rate limiting, and robust concurrent request queuing.
