## 配置说明
```
Domain Names ：填写网站域名，需要上面做好DNS解析，把域名绑定到服务器IP

Scheme ： 选择HTTP或HTTPS。默认http即可，除非有自签名证书

Forward Hostname/IP ：填写要代理到的目标主机名或IP地址，或者Docker容器内部IP（NPM和程序服务在同一台服务器上）

Forward Port：填写目标主机的端口号，这里是NPM管理界面81端口

Cache Assets ：缓存，根据需求选择打开

Block Common Exploits： 阻止常见的漏洞，根据需求选择打开

Websockets Support ：WS支持，根据需求选择打开

Access List： NPM自带的一个限制访问功能
```
