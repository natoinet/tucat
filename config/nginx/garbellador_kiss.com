server {
    listen      80;
    client_max_body_size 4G;
    server_name garbellador.com;
    charset     utf-8;

    keepalive_timeout 5;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }

    location /static/ {
        autoindex on;
        alias /home/antoinet/src/tucat/staticfiles/;
    }

    location = /favicon.ico  {
       rewrite "/favicon.ico" /staticfiles/images/favicon.ico;
    }

    location = /robots.txt  {
       rewrite "/robots.txt" /staticfiles/robots.txt;
    }

}

