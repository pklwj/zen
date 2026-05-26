##### 在 Nginx 上使用 Let's Encrypt 启用 HTTPS/SSL

要在 **Nginx** 上启用 **HTTPS**，您需要安装一个 **Certbot** 工具，该工具会自动从 Let's Encrypt 下载域的免费 SSL 证书。
```shell
sudo apt install certbot python3-certbot-nginx -y
```

运行此命令获取证书，并让 Certbot 自动编辑你的 nginx 配置来提供证书，在一步操作中开启 HTTPS 访问。
```shell
sudo certbot --nginx

```

##### 自动续订 Nginx 的 SSL 证书
Let's Encrypt 证书的有效期为 90 天，因此通过 cron 作业设置自动续订非常重要。
```shell
sudo crontab -e
```
将以下行添加到 crontab。
```bash
0 0 * * 0 /usr/bin/certbot renew --quiet
```
这将每周自动续订 SSL 证书，确保它在 90 天到期之前续订。
