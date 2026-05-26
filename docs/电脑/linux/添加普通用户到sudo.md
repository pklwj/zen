#debian 
如果由于任何原因，先前解释的方法无法将您的当前用户添加到 Debian 12 sudo 组中，则可以使用另一种方法。在此方法中，我们直接 **编辑** **Sudoers** **文件** 以 **添加用户** 。为此，请使用以下命令：

**如果您还没有，请切换到 root 用户。**

```bash
su root
```

### 在 Debian 12 上编辑 Sudoers 文件

现在，使用以下命令编辑 sudoers 文件。

```bash
nano /etc/sudoers
```

### 添加您的用户

滚动到文件末尾并添加以下行。

```bash
用户名 ALL=(ALL:ALL) ALL
```

**注意** ：将 **用户名** 替换为您要为 Debian 12 BookWorm 的 `sudo` 组添加的用户。

**例如** ，如果我们的用户名是 **linuxshout** ，则上述命令将如下所示：

```bash
linuxshout ALL=(ALL:ALL) ALL
```
![](https://picx.zhimg.com/v2-27a2bc06fb2f8609ed516cbca32997fd_1440w.jpg)

按下 **Ctrl + O** 保存文件，使用 **Ctrl + X** 键退出文件。

注销并重新登录以应用更改。之后，您将能够在 Debian 12 Linux 系统中使用 sudo 命令与您的当前用户。