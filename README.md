ACEest Fitness 💪

A Python-based fitness application with CI/CD integration using Docker and GitHub Actions.

🚀 Setup & Run Locally
git clone https://github.com/your-username/aceest-fitness.git
cd aceest-fitness

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
python app.py
🧪 Run Tests
pytest test_app.py -v
🐳 Docker Usage
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness

Run tests inside Docker:

docker run --rm aceest-fitness pytest test_app.py -v
🔄 CI/CD Overview
GitHub Actions

Pipeline includes:

Build & dependency installation
Linting using flake8
Docker image build
Automated testing using pytest inside Docker
Jenkins (High-Level Flow)
Pull code from GitHub
Install dependencies
Run linting & tests
Build Docker image
Deploy (optional)
📁 Project Structure
aceest-fitness/
├── app.py
├── test_app.py
├── requirements.txt
├── Dockerfile
✅ Features
Automated CI/CD pipeline
Dockerized application
Unit testing with pytest
Code quality checks
