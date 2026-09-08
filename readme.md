# Nano-Mind

![Language](https://img.shields.io/badge/language-C++%20%7C%20Python-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Focus](https://img.shields.io/badge/focus-Systems%20Engineering-red?style=for-the-badge)


# Live Demo

[![Deployed on HuggingFace](https://img.shields.io/badge/Deployed%20On-HuggingFace-b7fc1d?style=for-the-badge&logo=huggingface&logoColor=black)](https://not-omega-inference.hf.space/)


A blazing-fast **50M parameter Small Language Model** inference engine built from scratch in C++, served via a Python FastAPI backend.

> **Benchmark:** ~28 tok/s | ~35ms/token on Intel i3 11th Gen (8GB RAM, Windows 11)

## 🧠 How to get the Model Weights (`model.bin`)

To train the model and generate your own `model.bin` and `tokenizer.bin` files, simply open the Google Colab notebook below. It is fully optimized to train on Colab's Free Tier GPU (T4).

1. Open the notebook link below.
2. Change the runtime to **GPU** (`Runtime` > `Change runtime type` > `T4 GPU`).
3. Run all cells to train and export the binary weights.


[https://colab.research.google.com/drive/1UEjL2YZmyxs5ZkdxN_aPT8ceApb3a-Xx?usp=sharing](https://colab.research.google.com/drive/1UEjL2YZmyxs5ZkdxN_aPT8ceApb3a-Xx?usp=sharing)

---

<img width="1523" height="836" alt="image" src="https://github.com/user-attachments/assets/450013b5-7f1c-4b50-9fc4-a0d162896b76" />


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
