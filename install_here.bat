@echo off

python -m virtualenv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Installation successfull!
pause