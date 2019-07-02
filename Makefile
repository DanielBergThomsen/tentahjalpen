.EXPORT_ALL_VARIABLES:

FLASK_APP=tentahjalpen
FLASK_ENV=development

DATABASE_URL=postgresql://postgres:not_a_password@localhost:5432/courseData

dokku-frontend:
	git subtree push --prefix frontend dokku-frontend master


dev-front:
	cd frontend && npm start && cd ..


prod-front:
	cd frontend && serve -s build && cd ..


build-front:
	cd frontend && npm run-script build && cd ..


test-front:
	cd frontend && npm run-script test && cd ..


# needs backend to run tests with
cypress:
	cd frontend && ./node_modules/.bin/cypress open


# FRONTEND
# --------------------------------------------------
# BACKEND


dokku-backend:
	git subtree push --prefix backend dokku-backend master


dev-back:
	. backend/venv/bin/activate \
		&& cd backend \
		&& flask run --no-reload \
		&& cd ..


prod-back:
	gunicorn wsgi:app \
	--bind localhost:5000 \
	--workers 1 \
	--log-file - \
	--timeout 300


docker-back:
	docker build --tag=tentahjalpen_backend . \
	&& docker run -p 80:80 tentahjalpen_backend


manage-db:
	. backend/venv/bin/activate \
		&& cd backend \
		&& python backend/src/db_manager.py data.db \
		&& cd ..


test-back:
	. backend/venv/bin/activate \
		&& cd backend \
		&& python -m pytest \
		&& cd ..

lint-back:
	. backend/venv/bin/activate \
		&& cd backend \
		&& python -m pylint **/*.py \
		&& cd ..
