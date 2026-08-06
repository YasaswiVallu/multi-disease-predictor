# 🩺 VitalSense AI — Smart Multi-Disease Risk Predictor

VitalSense AI is a machine learning powered web application that screens for **Heart Disease**, **Diabetes**, and **Kidney Disease** risk, and includes an integrated **AI Health Assistant** chatbot for personalized follow-up guidance.

## 🚀 Features

- **Multi-Disease Screening** — Risk assessment for 3 diseases using trained Random Forest models
- **Interactive Multi-Page UI** — Clean navigation flow: Home → Disease Selection → Assessment
- **AI Health Assistant** — Chat-based Q&A powered by Llama 3.3 70B (via Groq API), context-aware of your screening result
- **Personalized Suggestions** — Risk-based health tips and next steps for each disease
- **Dark / Light Mode** — Toggle between themes
- **Animated, Modern UI** — Built with Streamlit + custom CSS

## 🧠 Machine Learning

| Disease | Model | Accuracy |
|---|---|---|
| Heart Disease | Random Forest Classifier | ~98.5% |
| Diabetes | Random Forest Classifier | ~73% |
| Kidney Disease | Random Forest Classifier | ~100%* |

*Trained on the UCI Cleveland Heart Disease, Pima Indians Diabetes, and UCI Chronic Kidney Disease datasets.*

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **ML:** scikit-learn (Random Forest), joblib
- **LLM Integration:** Groq API (Llama 3.3 70B)
- **Language:** Python

## 📂 Project Structure