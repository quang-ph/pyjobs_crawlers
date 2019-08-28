all:
	lint

lint:
	flake8 --exclude venv/,env/,rotate_useragent.py .

test:
	./runner

ci: lint
	./runner
