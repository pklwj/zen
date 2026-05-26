#docker


```yaml
services:
  filebrowser:
    container_name: filebrowser
    image: filebrowser/filebrowser
    restart: always
    volumes:
      - /docker/aria2/downloads:/srv/downloads
      - /srv/dev-disk-by-uuid-7b9e5892-c7b5-4085-bea9-83becee080fa:/srv/256g
      - /srv/dev-disk-by-uuid-080182f8-2289-4f4b-a6e3-7abbde56e84a:/srv/1t
      - /srv/remotemount/win/webdav:/srv/smb
    ports:
      - 8080:80
networks: {}
```

