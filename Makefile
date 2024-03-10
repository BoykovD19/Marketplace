check-format:
	pre-commit run -a
format: check-format
test:
	python manage.py test
