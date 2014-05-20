server {
    listen 80;
    server_name %(server_name)s %(server_alias)s;
    root %(docroot)s;
    client_max_body_size 20M;

    location / {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:%(port)s;
    }

    location /static {
        autoindex on;
    }
}
