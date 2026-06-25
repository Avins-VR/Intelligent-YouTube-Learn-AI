# 🎓 Intelligent YouTube Learn AI

## AI-Powered Educational Video Learning Assistant

🔗 Live Demo: https://intelligent-youtube-learn-ai.streamlit.app

---
> Transform any educational YouTube video into an intelligent learning experience using **Artificial Intelligence, NLP, RAG, LLMs, and Vector Databases**.

---

## 📖 Overview

The **AI-Powered Educational Video Learning Assistant** is an intelligent web application that converts educational YouTube videos into structured learning materials.

Instead of watching long video lectures repeatedly, students can simply provide a **YouTube URL**, and the system automatically generates:

- 📄 Video Summary
- 📝 Smart Notes
- 🧠 Concept Map
- ❓ MCQs (Easy, Medium & Hard)
- 🎯 Learning Recommendations
- 💬 AI Doubt Clarification (RAG Chatbot)

Additionally, users can download the generated **Summary**, **Notes**, and **MCQs** as **PDF files** for offline learning and revision.

---

# 🚀 Problem Statement

Millions of students learn from YouTube every day.

However, educational videos have several limitations.

## 1. Time-Consuming Learning

Students may watch a **1-hour lecture** just to understand **a few important concepts**, which consumes a significant amount of time.

---

## 2. No Structured Notes

Educational videos present information continuously.

Students must manually create:

- Notes
- Important Points
- Revision Material

This process is tedious and time-consuming.

---

## 3. Difficult to Understand Concept Relationships

Videos explain concepts sequentially.

Example:

```
Machine Learning
      ↓
Supervised Learning
      ↓
Regression
      ↓
Linear Regression
```

Students cannot easily visualize how concepts are connected.

---

## 4. No Self-Assessment

After completing a lecture, students often wonder:

> "Did I actually understand this topic?"

Traditional videos do not provide automatic assessments.

---

## 5. No Doubt Clarification

If students have questions like:

- What is Backpropagation?
- Why is Normalization important?

They must search again or rewatch the video.

---

## 6. No Learning Path Guidance

After finishing one topic, students often don't know:

> "What should I learn next?"

They spend additional time searching for the next relevant topic.

---

# 💡 Proposed Solution

The proposed system converts any educational YouTube video into an AI-powered interactive learning assistant.

The user simply provides:

```
YouTube Video URL
```

The system automatically:

- Extracts the transcript
- Understands the content
- Organizes knowledge
- Generates learning resources
- Answers user questions

---

# ⚙️ System Workflow

```
                  YouTube Video URL
                          │
                          ▼
              Transcript Extraction
                          │
                          ▼
                 Text Preprocessing
                          │
                          ▼
                  Text Chunking
                          │
                          ▼
              Embedding Generation
                          │
                          ▼
                  ChromaDB Storage
                          │
                          ▼
                   RAG Retrieval
                          │
                          ▼
                 Large Language Model
                          │
                          ▼
        ┌────────────────────────────────────┐
        │          Generated Outputs         │
        ├────────────────────────────────────┤
        │ 📄 Video Summary                   │
        │ 📝 Smart Notes                     │
        │ 🧠 Concept Map                     │
        │ ❓ MCQs (Easy / Medium / Hard)     │
        │ 🎯 Learning Recommendations        │
        │ 💬 Doubt Clarification             │
        └────────────────────────────────────┘
```

---

# ✨ Features

## 📄 Video Summary

Generates a concise summary of the complete lecture.

### Example

**Topic**

Machine Learning

**Summary**

Machine Learning is a subset of Artificial Intelligence that enables systems to learn from data without explicit programming.

### Benefits

- Saves time
- Quick understanding
- Faster revision

---

## 📝 Smart Notes

Automatically extracts:

- Important Concepts
- Definitions
- Key Points
- Revision Material

### Example

```
✔ Machine Learning
✔ Supervised Learning
✔ Regression
✔ Classification
```

### Benefits

- Easy revision
- Structured learning
- Saves note-taking effort

---

## 🧠 Concept Map

Generates a hierarchical visual representation of concepts.

Example

```
Artificial Intelligence
│
├── Machine Learning
│     ├── Regression
│     └── Classification
│
└── Deep Learning
      ├── CNN
      └── RNN
```

### Benefits

- Better conceptual understanding
- Visual learning
- Easier memorization

---

## ❓ MCQ Generation

Automatically generates assessment questions.

Difficulty Levels:

- 🟢 Easy
- 🟡 Medium
- 🔴 Hard

### Example

**Question**

Which learning algorithm uses labeled data?

A. Reinforcement Learning

B. Unsupervised Learning

C. Supervised Learning

D. Clustering

**Answer**

```
C. Supervised Learning
```

### Benefits

- Self-assessment
- Exam preparation
- Practice questions

---

## 🎯 Learning Recommendations

Suggests the next topics based on the current video.

Example

```
Current Topic

Machine Learning

Recommended Topics

1. Linear Regression
2. Logistic Regression
3. Decision Trees
4. Neural Networks
```

### Benefits

- Personalized learning path
- Continuous learning
- Saves search time

---

## 💬 AI Doubt Clarification

Students can ask questions related to the uploaded video.

### Example

**Question**

```
What is Overfitting?
```

**Answer**

```
Overfitting occurs when a machine learning model learns
the training data too closely and performs poorly on unseen data.
```

Generated using:

```
Question
     │
     ▼
RAG Retrieval
     │
     ▼
Relevant Transcript
     │
     ▼
LLM Response
```

### Benefits

- Interactive learning
- Video-specific answers
- Reduced hallucination

---

## 📥 PDF Export

Users can download:

- 📄 Summary
- 📝 Notes
- ❓ MCQs

as professionally formatted **PDF documents**.

---

# 🧠 Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| Streamlit | Web Application |
| YouTube Transcript API | Transcript Extraction |
| LangChain | LLM Workflow |
| ChromaDB | Vector Database |
| Sentence Transformers | Embedding Generation |
| RAG | Context-aware Question Answering |
| Groq LLM | Summary, Notes, MCQs & Chat |
| Mermaid.js | Concept Map Visualization |
| ReportLab | PDF Generation |

---

# 🛠 AI Technologies Used

## Text Preprocessing

The extracted YouTube transcript is cleaned and prepared before being processed by the AI models.

Used for:

- Removing unnecessary characters
- Normalizing whitespace
- Cleaning transcript text
- Preparing text for chunking

```
Raw Transcript
      │
      ▼
Cleaned Transcript
```

Purpose:

Prepare high-quality text for embedding generation and retrieval.

---

## Embedding Model

Converts text into numerical vectors.

Purpose:

Semantic understanding.

Example

```
AI

Artificial Intelligence

↓

Similar Meaning
```

---

## Vector Database

Stores embeddings inside **ChromaDB**.

```
Transcript
     │
     ▼
Embeddings
     │
     ▼
ChromaDB
```

---

## Retrieval-Augmented Generation (RAG)

Instead of answering from memory,

the system first retrieves relevant information.

```
User Question
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Provide Context
      │
      ▼
Generate Accurate Answer
```

Benefits

- Better Accuracy
- Less Hallucination
- Video-specific Responses

---

## Large Language Model (LLM)

Used for:

- Summary Generation
- Notes Generation
- MCQ Generation
- Recommendation Generation
- Doubt Clarification

---

# 📂 Project Structure

```
VIDEO-LEARNING-ASSISTANT/
│
├── .streamlit/
│
├── chroma_db/
│
├── pages/
│   ├── chat_page.py
│   ├── concept_map_page.py
│   ├── mcq_page.py
│   ├── notes_page.py
│   └── recommendations_page.py
│
├── utils/
│   ├── __init__.py
│   ├── exceptions.py
│   └── text_cleaning.py
│
├── .env
├── .gitignore
│
├── app.py
├── config.py
├── transcript.py
├── summary.py
├── notes.py
├── mcq.py
├── recommendations.py
├── concept_map.py
├── embeddings.py
├── rag.py
├── session_utils.py
├── ui_theme.py
├── test_transcript.py
│
├── requirements.txt
├── runtime.txt
│
└── README.md
```

---

# 🎯 Target Users

### 👨‍🎓 Students

- Summary
- Notes
- MCQs
- Revision

---

### 🔬 Researchers

- Fast lecture understanding
- Knowledge extraction

---

### 📚 Competitive Exam Aspirants

- Important concepts
- Practice questions
- Quick revision

---

### 🌍 Self Learners

- Personalized learning
- Structured learning path
- AI doubt support

---

# 🎯 Expected Outcome

Instead of spending:

```
⏳ 1 Hour Watching a Video
```

Students can obtain within a few minutes:

- 📄 Summary
- 📝 Notes
- 🧠 Concept Map
- ❓ MCQs
- 🎯 Learning Recommendations
- 💬 Doubt Clarification
- 📥 Downloadable PDFs

Resulting in a **faster, smarter, and more interactive learning experience**.

---

# 📦 Installation

Clone the repository

```bash
git clone https://github.com/your-username/VIDEO-LEARNING-ASSISTANT.git
```

Navigate to the project

```bash
cd VIDEO-LEARNING-ASSISTANT
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure environment variables

```env
GROQ_API_KEY=your_api_key
```

Run the application

```bash
streamlit run app.py
```

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

# 📜 License

This project is developed for educational and research purposes.

---

## 👨‍💻 Author

**Avins V R**  

AI & Data Science Student

AI/ML Developer 

GitHub:
https://github.com/Avins-VR

⭐ If you found this project useful, don't forget to **Star** this repository!
