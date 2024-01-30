python3 -m venv .venv
python3 -m pip install --upgrade pip

source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
