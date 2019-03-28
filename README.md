# staticblog
 一个基于Flask的静态博客，支持md语法
# 使用方法
 提前安装pipenv，用来配置虚拟环境  
 配置config.python中的信息，source文件夹下存放md文件，_posts为文章，_pages为页面
 >git clone https://github.com/birdmanwings/staticblog.git</br>
 >cd staticblog</br>
 >pipenv install --dev</br>
 >python run.py   
 
# 注意  
 md文开头需要配置meta头，否则会自动生成meta信息
 1. meta信息之间不能有空行，但与正文之间必须有至少一个空行；
 2. meta信息必须使用小写，并使用英文冒号；
 3. 非文章页面（即 page 页面文件）的meta信息必须包含title和url（如：about）信息；
 4. 如tag信息不只一个时，需换行并且至少有 4 个空格。
 ```
 title: Hello world // 文章标题
 summary: 第一篇文章 // 文章简介
 url: hello-world // 文章 url
 datetime: 2018-02-15 // 文章日期
 category: 随笔 // 文章分类
 tag: 测试 // 文章标签
     随笔

 正文开始
 ```
# 上传文件
 /admin管理员登录
