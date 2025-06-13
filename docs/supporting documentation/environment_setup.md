Environment Setup for KPATH Enterprise
======================================

This project uses pyenv with Python 3.10.13 and the torch-env virtual environment.

Prerequisites:
--------------
1. Install pyenv: https://github.com/pyenv/pyenv
2. Install Python 3.10.13: `pyenv install 3.10.13`
3. Create the virtual environment: `pyenv virtualenv 3.10.13 torch-env`

Activation:
-----------
To activate the environment:
```bash
pyenv activate torch-env
```

Or use the full Python path directly:
```bash
/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python
```

Running Scripts:
----------------
All scripts should be run with the torch-env environment active:

```bash
# Activate environment first
pyenv activate torch-env

# Then run scripts
python scripts/populate_enterprise_services.py
python scripts/rebuild_search_index.py

# Or use full path
/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python scripts/rebuild_search_index.py
```

Starting the Server:
--------------------
```bash
pyenv activate torch-env
python backend/main.py
```

Installing Dependencies:
------------------------
```bash
pyenv activate torch-env
pip install -r requirements.txt
```

Note: The torch-env includes PyTorch, Sentence-Transformers, FAISS, and other ML dependencies 
required for the semantic search functionality.
