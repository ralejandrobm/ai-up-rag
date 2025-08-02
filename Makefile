clean:
	find . | grep -E "(__pycache__$|\.pyc$|\.pyo$|.idea$)" | xargs rm -rf

dev:
	docker compose -p ai-up-odoo -f setup/docker-compose.yml up --build --remove-orphans

# prod commands
_prod_up:
	docker compose -p ai-up-odoo -f setup/docker-compose.yml up -d --build --remove-orphans

_prod_down:
	docker compose -p ai-up-odoo -f setup/docker-compose.yml down --remove-orphans

prod: _prod_down _prod_up

restart:
	docker compose -p ai-up-odoo -f setup/docker-compose.yml restart ai_up_odoo 

logs:
	docker compose -p ai-up-odoo -f setup/docker-compose.yml logs -f --tail=10

install-models:
	docker compose -p ai-up-odoo -f setup/docker-compose.yml exec ai_up_odoo python3 setup/install_models.py

# utils

clean_idea_cached_files:
	git rm -r --cached .idea/

install_hooks:
	pre-commit install

format:
	python -m black .

lint:
	python -m flake8

push: format lint

dev-deps:
	pip install -r requirements-dev.txt

prod-deps:
	pip install --no-dev -r requirements.txt
