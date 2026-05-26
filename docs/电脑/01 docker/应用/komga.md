# 元数据刮削
https://github.com/chu-shen/BangumiKomga
# docker compose

```yaml
version: '3'
services:
  bangumikomga:
    image: chu1shen/bangumikomga:main
    container_name: bangumikomga
    volumes:
    - /path/BangumiKomga/config.py:/app/config/config.py   # 内容更改见 step.2
    - /path/BangumiKomga/recordsRefreshed.db:/app/recordsRefreshed.db
    - /path/BangumiKomga/logs:/app/logs
    - /path/BangumiKomga/archivedata:/app/archivedata # 离线元数据（可选），详见`ARCHIVE_FILES_DIR`
```

# bangumi token
```
W0kff4FxeLhgX7TOYMLsOKVzXNCl1WCre24kf8M2
```
