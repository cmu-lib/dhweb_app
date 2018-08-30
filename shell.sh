docker build -t dhweb_image . 
docker container run -p 8000:8000 -i -t --rm dhweb_image bash
