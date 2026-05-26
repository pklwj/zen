#Linux #debian
## 1、设置静态ip

查看网卡名称是 **ens33**

```bash
ip address
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/2e1ee96bd5c3451b1a34b76d5b0fe338.png)

编辑 网卡配置 文件

```
nano /etc/network/interfaces
```

默认是这样的  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/11407f8510dc6d7cf855e4ea2dfd9358.png)

在最后面添加下面内容 其中

1. ens33是上步中查询到的网卡名称
2. address 192.168.2.157 是ip地址
3. netmask 255.255.255.0 是ip地址的子网掩码
4. gateway 192.168.2.2 是ip地址的网关
```bash
auto ens33
iface ens33 inet static
address 192.168.2.157
netmask 255.255.255.0
gateway 192.168.2.2
12345
```

编辑后的/etc/ [network](https://so.csdn.net/so/search?q=network&spm=1001.2101.3001.7020) /interfaces 文件内容如下

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/85086350b8d0f8d6b0c9af2cfd5fc086.png)

最后重启网络服务

```bash
systemctl restart networking.service
```

## 2、设置dns

debian 12安装后默认没有/etc/resolv.conf 文件  
建立此文件

```bash
vi /etc/resolv.conf
```

添加以下内容

```bash
nameserver 114.114.114.114
nameserver 8.8.8.8
nameserver 8.8.8.4
```

文件内容如下

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/25c51dfb018f91ec7e739526aecc9915.png)