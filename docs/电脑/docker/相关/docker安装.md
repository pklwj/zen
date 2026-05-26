#docker #debian 

​**更新系统软件包​**
```shell
sudo apt update && sudo apt upgrade -y
```
​**​安装依赖工具​**​
```shell
sudo apt install -y apt-transport-dockerhttps ca-certificates curl software-properties-common
```
### 二、配置国内镜像源（以清华源为例）
```shell
# 添加 Docker 官方 GPG 密钥（使用国内镜像加速下载）
curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 清华源仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
### 三、安装 Docker 引擎
```bash
# 更新软件源并安装核心组件
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证安装
sudo docker --version
sudo docker run hello-world  # 测试容器运行
```
