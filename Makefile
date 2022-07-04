run:
	poetry run python3 src/manage.py runserver

migrations:
	poetry run python3 src/manage.py makemigrations

migrate:
	poetry run python3 src/manage.py migrate

newsuperuser:
	poetry run python3 src/manage.py createsuperuser

test:
	poetry run python3 src/manage.py test -v 2 common events

dump_dummy_data:
	poetry run python3 src/manage.py dumpdata --format=json --indent=4 > populate.json

populate_dummy_data:
	poetry run python3 src/manage.py loaddata populate.json
