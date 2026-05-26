```yaml
services:
  navidrome:
    image: deluan/navidrome:latest
    user: 1000:1000 # should be owner of volumes
    ports:
      - "4533:4533"
    restart: unless-stopped
    environment:
      # Optional: put your config options customization here. Examples:
      # ND_LOGLEVEL: debug
    volumes:
      - "/path/to/data:/data"
      - "/path/to/your/music/folder:/music:ro"
```


# API account created

Here are the details of your new API account.

| **Application name** | lastfm                           |
| -------------------- | -------------------------------- |
| **API key**          | 0e195da0fee27e6d8fd7ae3ef129e87b |
| **Shared secret**    | 602c6d067c22cf2197e82501c83914b6 |
| **Registered to**    | ojbkcnm                          |

| **Application name** | spotify                          |
| -------------------- | -------------------------------- |
| Client ID            | e5089f47b18642598abd0ad412c0cd7e |
| Client secret        | bf5c9bd74c394095b3036f506ef75208 |

# 第三方播放器
#### [feishin](https://github.com/jeffvli/feishin) # 套壳浏览器
