# CarbonAI - Industrial Carbon Intelligence Platform

A full-stack AI web application designed to predict industrial carbon emissions using machine learning, built with FastAPI, React, and an XGBoost model. This is an enterprise-grade SaaS template featuring JWT authentication, persistent history tracking via SQLite, and real-time data visualizaton.

## Features

- **Machine Learning Integration**: Powered by an XGBoost regressor trained on the `trail_df.csv` dataset to accurately predict `tCO₂e` emissions.
- **Data Insights Analytics**: A dedicated React dashboard visualizing global dataset averages, operational peak bounds, and feature-to-emission Pearson Correlation matrices.
- **Secure Authentication System**: Built-in backend `POST /register` and `POST /login` endpoints utilizing `bcrypt` hashing and JWT tokens to authenticate users.
- **Persistent Prediction History**: Signed-in users have all their simulation inputs and AI-predicted emissions saved directly to a `carbon_app.db` SQLite database.
- **Modern Futuristic UI**: Professional UI built with Tailwind CSS, Framer Motion, and Glassmorphism design aesthetics.

---

## 🛠 Prerequisites

Before you start, make sure you have the following installed:
- **Python 3.10+**
- **Node.js (v18+) & npm**

---

## 🚀 How to Run the Application

The project is split into two parts: the Python **Backend** API and the React **Frontend**. You need to run both concurrently in separate terminal windows.

### 1. Setup the Backend (FastAPI + XGBoost)

Open your first terminal and navigate to the backend folder:

```bash
cd d:\CarbonAI_3\backend
```

**Step 1.1: Install Python Dependencies**
Install all required libraries (FastAPI, Uvicorn, Pandas, XGBoost, SQLAlchemy, Passlib, etc.):
```bash
pip install -r requirements.txt
```

**Step 1.2: Train the ML Model**
The platform is powered exclusively by the `trail_df.csv` dataset. You must train the serialized `model.pkl` file before launching the server:
```bash
python training_pipeline.py
```
*(You should see an output confirming the model was saved successfully).*

**Step 1.3: Start the Backend Server**
Launch the Uvicorn web server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API is now running at `http://localhost:8000`. You can view the automatic Swagger UI documentation at `http://localhost:8000/docs`.

---

### 2. Setup the Frontend (React + Vite)

Open a second terminal window and navigate to the frontend folder:

```bash
cd d:\CarbonAI_3\frontend
```

**Step 2.1: Install Node Dependencies**
```bash
npm install
```

**Step 2.2: Start the Development Server**
Launch the Vite React app:
```bash
npm run dev
```

The frontend will typically launch at `http://localhost:5173`. Open this URL in your web browser.

---

## 💻 Using the Platform

1. **Explore Data Insights**: Navigate to **Data Insights** in the top navigation bar to see live feature correlations and averages parsed directly from the CSV.
2. **Register an Account**: Click "Get Started" to create a new user account safely stored in the backend database.
3. **Simulate Emissions**: Go to the **Dashboard**, adjust the operational sliders (Energy, Production, Raw Materials), and click **Predict Emissions**.
4. **View History**: Scroll down on the Dashboard to see your newly generated prediction permanently saved to your account!
