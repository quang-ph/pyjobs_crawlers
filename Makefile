all:
	./runner

lint:
	flake8 --exclude env/,rotate_useragent.py .

ci: lint
	./runner
