# 🎵 Lo-Fi Mood Generator – 4th Place at Lo-Fi Hack Hackathon (SF) 🎨  

A **local-first** AI-powered website that generates **mood-based images** and **AI-generated music** to create the perfect ambiance.  

## 🌟 Overview  
This project is designed to help users set the **perfect mood** based on a simple **text prompt**. Whether you're **studying, working, or relaxing**, our system:  

✅ **Generates an image** that matches the mood using **Stable Diffusion API**.  
✅ **Selects an AI-generated music track** using **cosine similarity** with our embedded **music database**.  
✅ **Runs locally** to ensure privacy and **fast performance**.  

### **Example**  
📝 User types: `"studying peaceful"`  
🎨 The system **generates a calm, focused image**.  
🎵 The system **selects the most relevant lo-fi track** for deep focus.  

---

## 🔥 Features  
- **Local-First** – No cloud dependencies, everything runs on-device.  
- **React + Vite Frontend** – Fast and lightweight UI.  
- **AI-Powered Music Selection** – Uses **pre-generated embeddings** for instant track matching.  
- **Stable Diffusion API** – Creates **custom images** to match the mood.  
- **Cosine Similarity Matching** – Ensures the **best track for the user's vibe**.  
- **Hackathon-Winning Project** – Built in **24 hours**, placing **4th at Lo-Fi Hack SF!**  

---

## 🛠 Tech Stack  
- **Frontend:** React (Vite) + Tailwind CSS  
- **Backend:** Local-first architecture with an embedded database  
- **AI Models:**  
  - **Stable Diffusion API** (for image generation)  
  - **Sentence Transformers** (`all-MiniLM-L6-v2`) (for AI music selection)  
- **Database:** ChromaDB (for storing music embeddings)  

---

## 🚀 How It Works  
1. **User enters a mood prompt** (e.g., `"relaxing coffee shop"`).  
2. **System generates a matching image** using **Stable Diffusion API**.  
3. **User prompt is embedded** and compared with **pre-generated AI music embeddings**.  
4. **Most relevant AI-generated track** is selected based on **cosine similarity**.  
5. **User experiences a perfect AI-powered ambiance!** 🎶🎨  

---

## 🖥 Setup & Installation  

### **1️⃣ Clone the repository**  
```bash
git clone https://github.com/your-username/lofi-mood.git
cd lofi-mood
