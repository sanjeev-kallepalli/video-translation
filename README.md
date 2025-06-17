create virtual environment
`python -m venv .venv`
activate virtual environment
`.venv/Scripts/activate`
`cd app`
`pip install -r requirements.txt`
`pip install git+https://github.com/openai/whisper.git`
`uvicorn main:app --host 0.0.0.0 --port 9000`