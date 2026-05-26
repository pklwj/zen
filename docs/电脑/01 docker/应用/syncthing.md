# 反向代理后用不了
## ​​修改 GUI 绑定地址​​
编辑 ~/.config/syncthing/config.xml：
```xml
<gui>
    <address>0.0.0.0:8384</address>  <!-- 允许外部访问 -->
    <tls>off</tls>                    <!-- 由 Nginx 处理 SSL -->
</gui>
```

# 自建中继
relay://0.0.0.0:22067/?id=QQNYOG3-BEERVX3-EUXXWJF-Y6DNULK-7AT6CWY-OPZMYLE-RBI7XTP-4FCFEAK&networkTimeout=2m0s&pingInterval=1m0s&statusAddr=%3A22070

## 搭建方案
1. 本地设备同步（局域网内）：适合在家中或办公室中使用，所有设备都在同一个局域网内进行文件同步。
2. 个人服务器 + 远程设备同步：在个人服务器上搭建 Syncthing，并与外部的多个设备（如手机、笔记本等）进行文件同步。
3. NAS（网络附加存储）搭建 Syncthing：将 Syncthing 部署在 NAS 上，实现家庭或小型办公室的集中化存储和同步。
4. Docker 搭建 Syncthing：使用 Docker 容器来运行 Syncthing，实现轻量级部署和易于管理的环境。
5. 云服务器搭建 Syncthing：在云服务商（腾讯云，阿里云等）上搭建 Syncthing，以实现公网设备同步


## 跨公网配置（需中继服务器）​
### 部署

```bash
docker run -d \
  --name strelaysrv \
  -p 22067:22067 \
  -p 22070:22070 \
  syncthing/relaysrv:latest \
  -pools=""  # 禁用公共池
```

relay://<中继服务器IP>:22067/?id=<中继服务器ID>
​​获取中继 ID​​：通过 
```
docker logs strelaysrv
```
 查找 id= 字段
-p 22067:22067  同步中继服务器协议监听端口
-p 22070:22070  同步中继服务器服务状态监听端口

Syncthing 的 ​**​同步协议监听地址​**(**中继服务地址**)​ 是设备在网络中用于接收和发送同步数据的通信端点，其核心作用是为设备提供可被其他节点访问的网络接口和端口。以下是详细解析：

```
default,relay://<服务器 IP>:22067/?id=<中继服务 ID>
```


全局发现服务器： 即为发现服务地址，推荐为

```
default,https://<服务器 IP>:8443/?id=<发现服务 ID>
```
[[bf81e525dd462f306d161196c3177806_MD5.webp|Open: 202312101805967.webp]]
![[bf81e525dd462f306d161196c3177806_MD5.webp]]