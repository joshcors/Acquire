
init: install_libs

install_libs:
	pip install -e .
	pip install -r requirements.txt
	python src/Game/metadata.py
