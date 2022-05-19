# Vetty-task-api

This project is developed with python 3.10.2 on mac.

Move to directory Vetty-task-api
use pip to install all requirements .
Setup redis conf in config.py for local or development environment .
In production load .env via uvicorn --load-env param and clear default values in config,py

Run 
uvicorn app:app --port 8000
to start the server and visit localhost:8000/docs to test the api from FASTAPI docs.
