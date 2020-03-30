all:
	docker-compose up
detached:
	docker-compose up -d
stop:
	docker-compose stop app
down:
	docker-compose down
attach:
	docker-compose exec app bash
db:
	docker-compose exec postgres psql -U dh
restart:
	docker-compose restart app nginx
rebuild:
	docker-compose build --no-cache app nginx
wipe: stop
	docker-compose exec postgres psql -U dh -d postgres -c 'DROP DATABASE dh;'
	docker-compose exec postgres psql -U dh -d postgres -c 'CREATE DATABASE dh;'
	$(MAKE) restart
	docker-compose exec app python manage.py migrate
reload: wipe
	docker-compose exec app python manage.py loaddata /vol/data/json/dh.json
dumptest:
	docker-compose exec app python manage.py dumpdata --indent 2 -e admin.logentry -e auth.permission -e contenttypes -e sessions -o abstracts/fixtures/test.json
loadtest: wipe
	docker-compose exec app python manage.py loaddata abstracts/fixtures/test.json
test:
	docker-compose exec app python manage.py test --parallel 4
coverage:
	-docker-compose exec app coverage run manage.py test
	docker-compose exec app coverage html
nightly: wipe
	docker-compose exec app python manage.py loaddata /vol/data/backups/backup.json
