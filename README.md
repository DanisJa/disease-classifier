# 🏥 AI Health Consultant API

This is a FastAPI application that acts as a digital health consultant. It uses a transformer model (`cross-encoder/nli-deberta-v3-small`) to classify symptoms and optional health parameters into the most probable disease from a list of 100+ common conditions.

---

## 🚀 Features

- 🔎 **Zero-shot disease prediction** using user-entered symptoms
- 📋 Accepts optional health data: age, weight, height, blood pressure, temperature, gender
- 🧠 Uses HuggingFace Transformers for language inference
- 📂 Supports custom or predefined disease lists
- 🐳 Docker & Docker Compose support
- ♻️ Auto reload on code/disease file change (for development)

---

## 📁 File Structure

