# EcoSort AI: Intelligent Multimodal Waste Segregation & Circular Decision System

> **A Flagship Sustainability Project for the 1M1B AI for Sustainability Virtual Internship**  
> *In Collaboration with IBM SkillsBuild & AICTE*  
> **SDG Alignment:** Primary **SDG 12** (Target 12.5) | Secondary **SDG 11** & **SDG 13**

---

## ?? Project Overview

**EcoSort AI** is an end-to-end, camera-ready decision-support system designed to solve waste segregation failure on university campuses and in urban communities. 

### Why It Matters
On typical Indian college campuses, over **70% of recyclable plastic, metal, and paper is ruined** because of cross-contamination (e.g., pizza oil soaking into cardboard, dirty food wrappers tossed into clean paper bins). Furthermore, hazardous sharps (broken lab glassware, needles) and spent lithium batteries are frequently discarded improperly, causing severe cuts and fire hazards for frontline sanitation workers (*Safai Karamcharis*).

EcoSort AI solves this by delivering:
1. **Multimodal Computer Vision & Inspection:** Classifies items into official color-coded bins (Blue, Green, Red, Yellow) and flags contamination in real time.
2. **IBM Granite 3.0 RAG Pipeline:** Ingests Indian Solid Waste Management Rules 2016, E-Waste Rules 2022, and campus circular guidelines to answer natural language disposal questions with verified statutory citations.
3. **Real-time Lifecycle Carbon Engine:** Calculates exact environmental savings (kg $CO_2e$ averted, liters of water conserved, and kWh saved).
4. **Mandatory Responsible AI Framework:** Complies with Section 7 of the 1M1B guidelines across Fairness, Transparency, Ethics, and Privacy.

---

## ?? Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested with Python 3.12)
- Dependencies: `flask`, `pillow` (already installed)

### 1. Launch with One Click (Windows)
Double-click:
```bash
run_app.bat
```
*This starts the Flask server and opens the interactive dashboard in your browser at `http://127.0.0.1:5000`.*

### 2. Manual Terminal Launch
```powershell
cd C:\Users\ASUS\.gemini\antigravity\scratch\ecosort-ai
py -3.12 app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in any modern web browser.

---

## ??? Interactive Web Features

| Feature | Description |
| :--- | :--- |
| **?? Waste Scanner & Inspector** | Click any of the 6 pre-loaded real-world test items (PET bottle, greasy pizza box, banana peel, lithium battery, aluminum can, broken glass) or upload your own image. View instant bin recommendation, contamination warnings, and actionable instructions. |
| **?? IBM Granite RAG Assistant** | Chat with the AI consultant. Inspect the IBM Granite instruction prompt structure (`<|start_of_role|>system<|end_of_role|>...`) and see verified statutory citations. |
| **?? Campus Impact Dashboard** | View live session carbon offsets and interact with the **Campus Population Scale Simulator** (project annual tons diverted and economic savings for 500 to 25,000 students). |
| **??? Responsible AI Inspector** | View the 5-scenario visual robustness matrix, sanitation worker safety alerts, and EXIF privacy guarantees. |
| **?? Interactive Presentation Deck** | Built directly into the application at `/presentation` with 10 presentation slides, full speaker notes, keyboard navigation (`?` / `?`), and an instant **"Save as PDF"** button! |

---

## ?? Running Automated Tests

A comprehensive unit test suite is included to verify all AI pipelines:
```powershell
py -3.12 -m unittest tests/test_ecosort.py
```

---

## ?? Repository Structure

```
ecosort-ai/
??? README.md                      # Complete project overview & quickstart guide
??? PROJECT_REPORT.md              # Full academic submission report (1M1B / IBM / AICTE)
??? PRESENTATION_DECK.md           # 10-slide presentation text with speaker notes
??? run_app.bat                    # One-click Windows application launcher
??? app.py                         # Flask server & REST API endpoints
??? core/
?   ??? __init__.py                # Package initialization
?   ??? classifier.py              # Multimodal Vision & Contamination Classifier
?   ??? rag_engine.py              # IBM Granite RAG Pipeline & Knowledge Search
?   ??? impact_calculator.py       # Environmental LCA & Carbon Offset Engine
?   ??? responsible_ai.py          # Fairness, Explainability, Ethics & Privacy
?   ??? waste_knowledge_base.json  # Curated Indian SWM 2016 & Circular By-Laws
??? static/
?   ??? css/styles.css             # Modern emerald eco-theme styling
?   ??? js/main.js                 # Interactive client logic & API handlers
?   ??? sample_images/             # 6 pre-generated test sample images
??? templates/
?   ??? index.html                 # Main interactive web dashboard
?   ??? presentation.html          # Interactive slide presentation viewer
??? tests/
    ??? test_ecosort.py            # Automated unit test suite
```

---

