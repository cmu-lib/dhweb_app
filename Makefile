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
