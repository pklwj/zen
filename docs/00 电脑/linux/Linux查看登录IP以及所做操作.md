#debian 
## who

who - 是显示目前登录系统的用户信息。执行who命令可得知目前有那些用户登入系统，单独执行who命令会列出登入帐号，使用的终端机，登入时间以及从何处登入。  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/6acc69bae801fe863071940b9df50521.png)  
\-b, --boot 最近一次系统启动的时间  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/917c7b0c29289b9c516a425001542ed4.png)  
\-m：打印当前连接客户端使用的用户以及连接的客户端的IP，此参数的效果和指定"am i"字符串相同；  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/d6c355b952c150633d27d09d35481c42.png)

## w

w - 用于显示已经登陆系统的用户列表，并显示用户正在执行的指令。执行这个命令可得知目前登入系统的用户有那些人，以及他们正在执行的程序。单独执行w命令会显示所有的用户，您也可指定用户名称，仅显示某位用户的相关信息。  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/344dffbd9d46d3056898b1a8f8a35f54.png)

## last

last - 用于显示用户最近登录信息。单独执行last命令，它会读取/var/log/wtmp的文件，并把该给文件的内容记录的登入系统的用户名单全部显示出来。  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ec462e51ad070b9fa437130cfcfd43a4.png)  
\-n <显示列数>或-<显示列数>：设置列出名单的显示列数；  
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c70383b62a24f7830275f92b4d367254.png)