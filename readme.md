# Nano-Mind

![Language](https://img.shields.io/badge/language-C++%20%7C%20Python-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Focus](https://img.shields.io/badge/focus-Systems%20Engineering-red?style=for-the-badge)


## Live Demo

[![Deployed on HuggingFace](https://img.shields.io/badge/Deployed%20On-HuggingFace-b7fc1d?style=for-the-badge&logo=huggingface&logoColor=black)](https://not-omega-inference.hf.space/)

## System Architecture

<img width="1731" height="789" alt="image" src="https://github.com/user-attachments/assets/5c457323-ce10-4ead-a2ec-8d4466f0d5b2" />


<img width="858" height="799" alt="image" src="https://github.com/user-attachments/assets/21dce5ce-f08e-443c-bc41-8a6f055317d1" />


*Interactive Design Document: [HHD Design](https://app.eraser.io/workspace/RMsX2vhTVpB6uaZgnBqV?origin=share)*

## 📊 Benchmark Report
For full details, metrics, and hardware comparisons, you can view the complete [Benchmark Report](BENCHMARK_REPORT.md).



## 🏗️ Architecture

```
User / Browser
      │
      ▼
FastAPI Server (main.py)
      │  tiktoken tokenizer (encode prompt → token IDs)
      ▼
inference.exe  ◄── model.bin (GPT-2 style, 50M params)
      │  AVX2 SIMD + OpenMP parallelism
      ▼
Token IDs → FastAPI → tiktoken decode → JSON response
```

**Stack:**
- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **Inference Engine:** C++17 with AVX2 SIMD + OpenMP (compiled to `inference.exe`)
- **Tokenizer:** tiktoken (GPT-2 encoding, 50,257 vocab)
- **Model:** Custom GPT-2-style binary format (`model.bin`)

---

## 🚀 Performance

| Metric | Value |
|---|---|
| Avg Request Latency | ~3556 ms / 100 tokens |
| Per Token Latency | ~35.57 ms/token |
| Throughput | **~28.12 tokens/sec** |
| Hardware | Intel i3-11th Gen, 8GB RAM |
| Platform | Windows 11 |

---

## 📁 Project Structure

```
INFERENCE ENGINE/
├── inference.cpp       # C++ inference engine (AVX2 + OpenMP)
├── inference.exe       # Compiled binary (Windows)
├── main.py             # FastAPI server
├── benchmark.py        # Performance benchmarking script
├── index.html          # Simple frontend UI
├── model.bin           # Model weights (binary format)
├── tokenizer.bin       # Tokenizer data
├── requirements.txt    # Python dependencies
├── SETUP_GUIDE.md      # Full setup instructions
└── .gitignore
```



## 📄 License

MIT License — free to use, modify, and distribute.
