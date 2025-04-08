# 🌱 Sustainable Habits Tracker API

Built by **João Pedro Carvalho**

A modern RESTful API built with **FastAPI** to help users track and improve their sustainable habits. Features include secure authentication, habit creation, daily tracking, and automatic reporting — all containerized with Docker and ready for CI/CD.

---

## 🔧 Features

- ✅ **User Authentication** using JWT
- ✅ **Create and Track Habits**
- ✅ **Weekly & Monthly Summaries**
- ✅ **FastAPI Docs Interface**
- ✅ **Dockerized & CI/CD Ready**

---

## 🚀 Tech Stack

- **Backend:** Python 3.10, FastAPI
- **Database:** SQLite + SQLAlchemy ORM
- **Auth:** OAuth2 + JWT
- **Containerization:** Docker
- **CI/CD:** GitHub Actions

---

## 🧪 Tutorial: Run and Use the API

### 🔹 Step 1: Clone the Repository

```bash
git clone https://github.com/johncarvalhonx/sustainable-habits-tracker.git
cd sustainable-habits-tracker
```

### 🔹 Step 2: Run Locally with Python

> Make sure you have Python 3.10+ and `pip` installed.

1. *(Optional but recommended)* Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the API:

```bash
uvicorn main:app --reload
```

4. Open your browser at:\
   👉 [http://localhost:8000/docs](http://localhost:8000/docs)\
   to test all endpoints with Swagger UI.

---

### 🐳 Step 3: Run with Docker (Optional)

> Make sure Docker is installed and running on your machine.

1. Build the image:

```bash
docker build -t sustainable-habits-tracker .
```

2. Run the container:

```bash
docker run -d -p 8000:8000 sustainable-habits-tracker
```

3. Access the docs at:\
   👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 Example API Usage (with `curl`)

### 🔐 Sign Up

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 🔓 Log In

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

Copy the token from the response and use it in the following requests:

```bash
Authorization: Bearer <your_jwt_token>
```

### 🌱 Create a Habit

```bash
curl -X POST http://localhost:8000/habits \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Recycle", "description": "Recycle paper and plastic"}'
```

### 📅 Track a Habit

```bash
curl -X POST http://localhost:8000/track \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"habit_id": 1}'
```

### 📊 Get Weekly/Monthly Summary

```bash
curl -X GET http://localhost:8000/summary \
  -H "Authorization: Bearer <your_jwt_token>"
```

---

## 🤖 Continuous Integration with GitHub Actions

This project includes a CI pipeline that:

- Installs dependencies
- Lints the code using `flake8`
- Runs basic tests using `pytest`

📄 **Workflow file:** `.github/workflows/ci.yml`

To add tests, create a `tests` folder with a file like:

```python
# tests/test_dummy.py
def test_dummy():
    assert 1 + 1 == 2
```

Then run:

```bash
pytest
```

---

## 🧠 Ideas for Future Features

- 🌍 PostgreSQL support
- 📧 Email reports via Celery
- 📱 Frontend dashboard (React or mobile app)
- 📈 Charts and analytics
- 🔐 Admin panel

---

## 👨‍💻 Author

**João Pedro Villas Boas de Carvalho**\
Computer Science Student @ UNIP – Brazil\
📧 [joaopedrovillasboascarvalho@gmail.com](mailto\:joaopedrovillasboascarvalho@gmail.com)\
📎 www.linkedin.com/in/joaopedrovbcarvalho

If something is wrong, don't hesitate to tell me!

---

## 📜 License

This project is licensed under the MIT License.
