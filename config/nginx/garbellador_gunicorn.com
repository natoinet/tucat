server {
    listen 80;
    client_max_body_size 4G;
    server_name garbellador.com;

    keepalive_timeout 5;

    # path for static files
    root /home/antoinet/src/tucat/staticfiles/;

    location / {
        # checks for static file, if not found proxy to app
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;

        proxy_pass   http://127.0.0.1:8000;
    }

    #For favicon
    location = /favicon.ico {
       rewrite "/favicon.ico" /staticfiles/images/favicon.ico;
    }

    #For robots.txt
    location = /robots.txt {
	rewrite "/robots.txt" /staticfiles/robots.txt;
    }

    error_page 500 502 503 504 /500.html;
        location = /500.html {
        root /home/antoinet/src/tucat/staticfiles/;
    }
}

