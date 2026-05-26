#debian 
### 临时

```bash
export http_proxy=http://192.168.31.245:10809
```

```bash
export https_proxy=http://192.168.31.245:10809
```
___
### 永久
```bash
1. nano /etc/profile
2. http_proxy=http://192.168.31.245:10809 #代理程序地址
3. https_proxy=http://192.168.31.245:10809
4. http_proxy=http://192.168.31.245:10809
5. export http_proxy
6. export ftp_proxy
7. export https_proxy

```
___
### 取消
而对于要取消设置可以使用如下命令，其实也就是取消环境变量的设置：
```bash
unset http_proxy
unset https_proxy
unset ftp_proxy
unset no_proxy
```
