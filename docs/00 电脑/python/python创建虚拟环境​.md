#python
```bash
# 创建虚拟环境
python3 -m venv env

# 激活环境
source env/bin/activate

# 安装依赖
pip install -r requirements.txt

```

### 更换国内镜像源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```


```
huggingface-cli download --resume-download immich-app/XLM-Roberta-Large-Vit-B-16Plus --local-dir immich
```

./hfd.sh immich-app/XLM-Roberta-Large-Vit-B-16Plus