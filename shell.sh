docker build -t dhweb_image .
docker container run -p 8000:8000 -v ~/Development/dh_abstracts/dh_web/app:/usr/src/app -i -t --rm dhweb_image bash
