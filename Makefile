all:
	lint

lint:
	flake8 --exclude env/,rotate_useragent.py .

test:
	./runner

ci: lint
	./runner
