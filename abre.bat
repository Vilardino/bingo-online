@echo off
powershell -ExecutionPolicy RemoteSigned -Command "& {call venv\Scripts\activate; streamlit run bingo.py}"
pause