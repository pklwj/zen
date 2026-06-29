# Linux mint 虚拟机
## 整体架构
```
virt-manager（图形界面）
        ↓
libvirt（管理层）
        ↓
QEMU（虚拟机模拟器）
        ↓
KVM（CPU硬件加速）
```

## 安装基础组件
```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients virt-manager bridge-utils
```

### KVM/QEMU 核心组件说明

* **`qemu-kvm`**：**虚拟化底层引擎**。结合 KVM 内核模块与 QEMU 模拟器，利用硬件加速让虚拟机获得接近原生的性能。
* **`libvirt-daemon-system`**：**后台核心服务**。在系统后台运行 `libvirtd` 进程，负责控制虚拟机生命周期、分配硬件资源、管理网络和存储。
* **`libvirt-clients`**：**命令行管理工具**。提供终端交互命令（如 `virsh`），用于在命令行中对虚拟机进行精细化配置与管理。
* **`virt-manager`**：**图形化管理器**。提供直观的桌面 GUI 窗口界面（如“图片.png”中所示的虚拟机管理器），方便用户创建、监控和操作虚拟机。
* **`bridge-utils`**：**网络桥接配置工具**。用于创建和管理虚拟网桥，让虚拟机可以直接接入宿主机所在的物理局域网，获取独立 IP。

## 配置用户权限
```bash
sudo adduser $USER libvirt
sudo adduser $USER kvm
```

验证并启动虚拟化服务
```bash
sudo systemctl status libvirtd
sudo systemctl enable --now libvirtd
```

## 安装windows
⭐ win10 LTSC
### CPU
- 4核
- host-passthrough
### 内存
| RAM  | VM分配    |
| ---- | ------- |
| 8GB  | 3–4GB   |
| 16GB | 4–6GB ⭐ |
| 32GB | 6–8GB   |
### 磁盘
- bus：VirtIO
- cache：none
- io：native
- discard：enabled

- 光驱

| 设备     | 内容        |
| ------ | -------------- |
| CDROM1 | Windows ISO    |
| CDROM2 | virtio-win.iso |

- virtio-win.iso下载地址 https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/

### GPU
型号：`QXL`

## 安装完后优化
**virtio-win驱动安装**
| 分类      | 名称                   | 是否必须   | 作用                  |
| ------- | -------------------- | ------ | ------------------- |
| 💽 存储驱动 | viostor / vioscsi    | ⭐ 必装   | 让Windows识别虚拟硬盘      |
| 🌐 网络驱动 | NetKVM               | ⭐ 必装   | 让Windows联网          |
| 🧠 内存优化 | balloon              | ⭐ 推荐   | 动态回收内存              |
| ⚙️ 系统增强 | qemu-ga（Guest Agent） | ⭐ 强烈推荐 | 时间同步/关机/状态管理        |
| 🎮 显示驱动 | QXL / virtio-gpu     | 可选     | 提升显示体验              |
| 📁 文件共享 | virtio-fs            | 可选（高级） | Linux ↔ Windows高速共享 |

### 文件共享
- **VirtIO-FS**
虚拟机内必须安装 `WinFSP.msi`
启动服务`VirtIO-FS Service`

- 调节电源：高性能
- 安装`spice-guest-tools`