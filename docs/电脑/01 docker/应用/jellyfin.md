# 镜像
**nyanmisaka/jellyfin**
# compose.yaml
```yaml
services:
  jellyfin:
    image: nyanmisaka/jellyfin:latest
    container_name: jellyfin
    environment:
      TZ: Asia/Shanghai
      PUID: 0
      PGID: 0
    volumes:
      - /docker/jellyfin/config:/config
      - /docker/jellyfin/cache:/cache
      - /srv/dev-disk-by-uuid-7b9e5892-c7b5-4085-bea9-83becee080fa/media:/media/movie:ro
      - /srv/dev-disk-by-uuid-7b9e5892-c7b5-4085-bea9-83becee080fa/H:/h:ro
      - /srv/dev-disk-by-uuid-7b9e5892-c7b5-4085-bea9-83becee080fa/music/音乐:/media/music:ro
    devices:
      - /dev/dri:/dev/dri
    restart: unless-stopped
    network_mode: host
networks: {}
```

# 硬件解码
- ​**​Linux​**​：AMD AMF 或 ​**​VA-API​**​（需核显驱动支持）

# TMDB刮削
#### 修改hosts
```
2600:9000:2721:f600:10:db24:6940:93a1 tmdb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 image.tmdb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 images.tmdb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 api.tmdb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 files.tmdb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 themoviedb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 api.themoviedb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 www.themoviedb.org #UHE_
2600:9000:2721:f600:10:db24:6940:93a1 auth.themoviedb.org #UHE_
```

# 登入Jellyfin容器

```shell
docker exec -it jellyfin /bin/bash
```
