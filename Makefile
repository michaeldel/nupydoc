dep:
	poetry install --no-root

test:
	poetry run pytest

clean:
	find . -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

.PHONY: dep test clean

