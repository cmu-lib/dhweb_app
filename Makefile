all:
	docker-compose up
stop:
	docker-compose stop dh-web
attach:
	docker-compose exec dh-web bash
db:
	docker-compose exec dh-postgres psql -U dh
restart:
	docker-compose restart dh-web dh-nginx
rebuild:
	docker-compose build --no-cache dh-web
wipe: stop
	docker-compose exec dh-postgres psql -U dh -d postgres -c 'DROP DATABASE dh;'
	docker-compose exec dh-postgres psql -U dh -d postgres -c 'CREATE DATABASE dh;'
	$(MAKE) restart
reload: wipe
	docker-compose exec dh-web python manage.py loaddata /vol/data/json/bkp.json
