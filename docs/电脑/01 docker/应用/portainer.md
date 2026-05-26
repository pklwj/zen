步骤 1：安装 Docker
curl -fsSL https://get.docker.com | bash -s docker
步骤 2：拉取 Portainer 英文版
docker pull portainer/portainer-ce:latest
步骤 3：启动 Portainer
docker run -d --name portainer -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v /app/portainer_data:/data --restart always --privileged=true portainer/portainer-ce:latest
步骤 4：访问 Portainer Web 界面
http://localhost:9000/
Docker Portainer CE 中文版
docker pull 6053537/portainer-ce
创建数据卷
docker volume create portainer_data
步骤 3：启动 Portainer
docker run -d --name portainer -p 9000:9000 --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data 6053537/portainer-ce
步骤 4：访问 Portainer Web 界面
http://localhost:9000/

