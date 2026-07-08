#ip #网络安全 #Linux #防火墙
# 一、核心配置步骤​​
### 1. ​​获取国内IP列表​​

国内IP段可通过APNIC或IANA的公开数据获取，使用脚本自动解析并生成IP集合文件：
```bash
wget --no-check-certificate -O- 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest' | \
awk -F\| '/CN\|ipv4/ { printf("%s/%d\n", $4, 32-log($5)/log(2)) }' > /etc/china.txt
```
此脚本会生成包含国内IPv4地址段的<font color="#f79646">/etc/china.txt</font>文件

### 2. ​​创建并加载IP集合​​

通过firewalld的ipset功能管理国内IP：
```bash
#创建名为"china"的IP集合（类型为哈希网络）
firewall-cmd --permanent --new-ipset=china --type=hash:net

#加载IP列表到集合
firewall-cmd --permanent --ipset=china --add-entries-from-file=/etc/china.txt

#补充内网IP段（根据实际需求调整）
firewall-cmd --permanent --ipset=china --add-entry='192.168.0.0/16'
firewall-cmd --permanent --ipset=china --add-entry='172.16.0.0/12'
firewall-cmd --permanent --ipset=china --add-entry='10.0.0.0/8'
```

### 3. ​​配置富规则放行国内IP​​

针对特定端口（如SSH的22端口和自定义端口40001）设置访问规则：
```bash
# 允许国内IP访问TCP 40001端口
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source ipset="china" port port="22000" protocol="tcp" accept'

# 允许国内IP访问UDP 40001端口
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source ipset="china" port port="22000" protocol="udp" accept'

# 开放其他端口范围（如40002-40010的TCP端口）
firewall-cmd --permanent --zone=public --add-port=40002-40010/tcp
```

### 4. ​​默认拒绝所有其他流量​​

确保未匹配规则的IP被拒绝：
```bash
# 移除默认允许的SSH服务（若需限制SSH访问，需单独配置）
firewall-cmd --permanent --zone=public --remove-service=ssh

# 设置默认策略为拒绝
firewall-cmd --permanent --zone=public --set-target=DROP
```

### 5. ​​生效配置​​

```bash
firewall-cmd --reload
```

# ​​二、关键注意事项​​
### 1. ​​IP列表更新​​
- 国内IP段可能动态变化，建议定期运行脚本更新/etc/china.txt，并通过firewall-cmd --reload同步规则。
### 2. ​​内网IP兼容性​​
 - 若服务器位于内网（如192.168.x.x），需在IP集合中显式添加内网段，避免本地通信中断1。
### 3. ​​协议与端口细化​​
- 若需同时放行TCP和UDP，需分别添加规则（如步骤3）。
- 使用firewall-cmd --list-rich-rules验证规则是否生效。
### 4. ​​日志与调试​​
- 启用防火墙日志以排查误拦截：
```bash
firewall-cmd --set-log-denied=all
```
- 检查日志文件：journalctl -u firewalld | grep DROP
### 5.定期检查规则完整性
```bash
firewall-cmd --list-all
```
