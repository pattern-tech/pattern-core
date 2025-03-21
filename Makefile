watch:
	python3 scripts/create_postgres_database.py
	python3 -m uvicorn src.main:app --host 0.0.0.0 --reload

prod:
	python3 scripts/create_postgres_database.py
	python3 -m uvicorn src.main:app --host 0.0.0.0