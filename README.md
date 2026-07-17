# mini-rag
Requirements
Python 3.8 or later
Install Dependencies
sudo apt update
sudo apt install libpq-dev gcc python3-dev
Install Python using MiniConda
Download and install MiniConda from here
Create a new environment using the following command:
$ conda create -n mini-rag python=3.8
Activate the environment:
$ conda activate mini-rag
(Optional) Setup you command line interface for better readability
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
(Optional) Run Ollama Local LLM Server using Colab + Ngrok
Check the notebook + Video
Installation
Install the required packages
$ pip install -r requirements.txt
Setup the environment variables
$ cp .env.example .env
Set your environment variables in the .env file. Like OPENAI_API_KEY value.

Run Docker Compose Services
$ cd docker
$ cp .env.example .env
update .env with your credentials
$ cd docker
$ sudo docker compose up -d
Run the FastAPI server
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
POSTMAN Collection
Download the POSTMAN collection from /assets/mini-rag-app.postman_collection.json


