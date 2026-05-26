# Tailscale子网路由（Subnet routers）功能部署

## 子网路由
简单文字描述这个功能，约等于就是个跳板机：

- 局域网内有很多个服务器
- 这些机器在内网都用`192.168.*.*`ip进行访问
- 并不是每台机器都能装tailscale
- 在一台机器上部署tailscale，开启subnet routers，通过这台机器，在已经用tailscale组网的机器上，可以直接用`192.168.*.*`ip访问内网的机器

看上去还是比较拗口，那就直接看官网的图片解释吧
![[Pasted image 20250608204901.png]]

# 开启ip转发

使用子网路由功能必须开启本机的ip转发。

这里以linux为例，这里直接照搬官网内容：

如果你的linux系统存在`/etc/sysctl.d`目录，使用如下命令：

```
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

否则使用如下命令：

```
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p /etc/sysctl.conf
```

> 第三步：启动tailscale，广播子网路由

命令如下

```
sudo tailscale up --advertise-routes=192.168.1.0/24
```

注意路由的网段，根据自己的情况调整即可。

比如

```
sudo tailscale up --advertise-routes=192.168.0.0/24,192.168.1.0/24
```

我的内网所有机器使用的都是`192.168.1.0/24`网络，所以只广播这一个网段。

> 第四步：网页端开启subnet routers功能

在第三步中，使用`tailscale up`启动tailscale以后，会跳出链接要求绑定到账号，这里不做赘述。

绑定成功以后，在官网管理台找到机器，点击右边三个点号出现菜单，选择`edit route settting`。

![](https://img.311803.xyz/2024/01/28/z85u88-0.png)

在下一窗口子网路由的网段，保存。

![](https://img.311803.xyz/2024/01/28/zanx3r-0.png)

到此，tailscale子网路由的功能部署完毕。在另外一台安装了tailscale并加入组网的机器上，就可以直接通过`192.168.1.*`的内网ip直接访问内网服务了。




```bash
tailscale up --advertise-routes=192.168.100.0/24
```
