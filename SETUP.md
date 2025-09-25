## Setup

Recommended: Python 3.12 via pyenv, local-only pipeline (rules + spaCy NER).

### 1) Prereqs (macOS)
```
brew install pyenv
```

### 2) Create Python 3.12 venv
```
pyenv install -s 3.12.6
pyenv local 3.12.6
python3 -m venv .venv312
source .venv312/bin/activate
python -m pip install -U pip
```

### 3) Install dependencies
```
python -m pip install -r python_backend/requirements.txt -r python_backend/requirements-dev.txt
python -m spacy download en_core_web_sm
```

### 4) Run tests
```
python -m pytest python_backend/tests -q
```

### Optional native deps
- libpostal is currently NOT required; address detection uses NER+heuristics.
- OCR (Tesseract) may be added later for scanned PDFs.


