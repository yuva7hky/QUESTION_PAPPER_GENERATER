# 📄 Question Paper Generation System

A full-stack web application that automates the generation of **CIE-I**, **CIE-II**, and **Model Examination** question papers from a structured Question Bank. The system intelligently selects questions based on predefined examination rules and generates professional question papers in both **PDF** and **DOCX** formats.

---

## 📌 Overview

The **Question Paper Generation System** is designed to simplify the process of preparing examination question papers for faculty members. Instead of manually selecting questions, the faculty uploads a structured Question Bank, selects the examination type, and the system automatically generates a complete question paper following the official examination pattern.

The application ensures that every newly generated question paper is unique by avoiding previously generated question combinations.

---

## ✨ Features

- 📂 Upload Question Bank (.docx)
- 🎯 Automatic Question Parsing
- 📝 Supports Multiple Examination Types
  - CIE-I (50 Marks)
  - CIE-II (50 Marks)
  - Model Examination (100 Marks)
- 🔄 Generate Unique Question Papers
- 🔁 Generate Another Question Paper without re-uploading
- 👀 Live Question Paper Preview
- 📄 Download as PDF
- 📄 Download as DOCX
- 🎓 Professional Examination Paper Layout
- 📱 Responsive User Interface

---

## 🛠 Tech Stack

### Frontend
- React.js
- Tailwind CSS
- Axios

### Backend
- Python
- Flask
- Flask-CORS

### Libraries
- python-docx
- ReportLab
- Random
- UUID
- Hashlib
- Regular Expressions (re)

---

## 📂 Project Structure

```text
Question-Paper-Generation-System/

├── frontend/
│   ├── src/
│   ├── components/
│   ├── App.jsx
│   └── ...
│
├── backend/
│   ├── app.py
│   ├── parser.py
│   ├── selector.py
│   ├── generator.py
│   ├── pdf_generator.py
│   ├── docx_generator.py
│   └── utils.py
│
├── uploads/
├── generated/
├── README.md
└── .gitignore
```

---

## ⚙️ How It Works

1. Upload a structured **Question Bank (.docx)**.
2. Select the examination type:
   - CIE-I
   - CIE-II
   - Model Examination
3. Click **Generate Question Paper**.
4. The system:
   - Parses the uploaded document.
   - Identifies Part A, Part B, and Part C.
   - Randomly selects questions according to the examination rules.
   - Ensures that the generated paper is unique.
5. Review the generated question paper in the preview section.
6. Download the final paper as **PDF** or **DOCX**.

---

## 📋 Examination Types

| Examination | Maximum Marks |
|-------------|---------------:|
| CIE-I | 50 |
| CIE-II | 50 |
| Model Examination | 100 |

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/Question-Paper-Generation-System.git
```

### Navigate to the Project

```bash
cd Question-Paper-Generation-System
```

---

## ▶️ Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## ▶️ Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

python app.py
```

---

## 📸 Screenshots

You can add screenshots of:

- Home Page
- Upload Question Bank
- Generated Question Paper Preview
- PDF Download
- DOCX Download

---

## 🎯 Future Enhancements

- User Authentication
- Faculty Login
- Admin Dashboard
- Database Integration
- Question Bank Management
- Automatic Bloom's Taxonomy Validation
- AI-assisted Question Recommendation
- Multiple University Templates
- Cloud Deployment

---

## 👨‍💻 Author

**Shridhar G**

Computer Science and Engineering

Jeppiaar Institute of Technology

GitHub: https://github.com/ShridharGomathisankar

---

## 📜 License

This project is developed for educational and academic purposes.

---

## ⭐ Acknowledgements

This project was developed to simplify and automate the process of generating examination question papers while maintaining professional formatting and examination standards.
