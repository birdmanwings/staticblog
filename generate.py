"""利用md文件生成html静态页面"""

import codecs
import shelve
from datetime import datetime

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader

from config import *


class Generate(object):

    def __init__(self):
        self._generated_folder = GENERATED_PATH  # 转换为html文件的存储位置
        self._post_folder = POST_PATH  # 存储文章的路径
        self._page_folder = PAGE_PATH  # 储存页面的路径
        self._posts = []  # 存储文章的meta信息
        self._pages = []  # 存储页面
        self._tags = []  # 存储标签
        self._categories = []  # 存储目录
        self.env = Environment(loader=FileSystemLoader("./staticblog/templates"))  # 模板的存放位置

    @property  # property装饰器让class不需要实例化就可以调用期中的函数
    def default_adder_id(self):  # 用来添加默认id(自增的)
        try:
            max_id = self._posts[-1].get('id') + 1
        except:
            max_id = 100
        return max_id

    def dump_data(self):  # shelve模块存储博客的数据
        dat = shelve.open(BLOG_DAT)
        dat['post_data'] = self._posts
        dat['page_data'] = self._pages
        dat['tag_data'] = self._tags
        dat['category_data'] = self._categories
        dat.close()

    def load_folder(self, folder):  # 打开文件夹并取出一个md文件
        for root, dirs, files in os.walk(folder):
            for name in files:
                if os.path.splitext(name)[1].lower() == '.md':
                    md = os.path.join(root, name)
                    yield md

    def save_html(self, file, html, file_type, year=None, month=None, extra_path=None):

        try:
            path = os.path.join(file_type, year, month)
        except:
            if extra_path:
                path = os.path.join(file_type, extra_path)
            else:
                path = file_type  # 这个path是generated文件夹下面的

        generated = os.path.join(self._generated_folder, path)  # 完整路径在static文件夹下面
        filename = os.path.splitext(file)[0] + '.html'
        if file_type == 'post':
            filename = self._set_post_filename(filename) + '.html'
        if not os.path.exists(generated):  # 如果没有文件夹存在，就创建
            os.makedirs(generated)
        with codecs.open(generated + '/' + filename, 'w', 'utf-8') as f:  # 写入html文件
            f.write(html)

    def _set_post_filename(self, filename):  # 根据文件名查询文件的meta元素，从而获取到url设置文章的文件名为其url
        filenames = [p['filename'] for p in self._posts]
        index = filenames.index(filename)
        url = self._posts[index]['url']

        return url

    def update_post_data(self, file, data):  # file传入为.md文件，data存放的为meta信息
        generate_file = os.path.splitext(os.path.basename(file))[0] + '.html'
        data['filename'] = generate_file  # 更新文件名
        self._posts.append(data)
        self.render_tag_posts(data['tag'])
        self.render_cate_posts(data['category'])
        self.render_index_html()

    def update_page_data(self, file, meta):  # 更新page页面的信息
        generate_file = os.path.splitext(os.path.basename(file))[0] + '.html'
        meta['filename'] = generate_file
        self._pages.append(meta)

    def markdown_to_html(self, file, file_type):
        """
        将 markdown 文件转换为 html
        :param file: markdown file  xxx.md
        """
        with codecs.open(file, mode="r", encoding="utf-8", errors='ignore') as f:
            body = f.read()
            md = Markdown(extensions=['fenced_code', 'codehilite(css_class=highlight,linenums=None)',
                                      'meta', 'admonition', 'tables'])
            content = md.convert(body)
            meta = md.Meta if hasattr(md, 'Meta') else {}  # 如果存在meta属性就获取一个dict,否则返回一个空的dict

            if file_type == 'post':
                data = self.parse_meta(file, meta)
                self.update_post_data(file, data)

                template = self.env.get_template('post.html')  # 获得这个模板的html文件后传入content,meta数据，title再进行渲染
                html = template.render(
                    article=content,
                    data=data,
                    title=data.get('title')
                )
                return html
            elif file_type == 'page':
                url = meta['url'] or os.path.splitext(file)[0]
                meta['url'] = url
                self.update_page_data(file, meta)

                template = self.env.get_template('page.html')
                html = template.render(
                    page=content,
                    title=meta.get('title')[0] or os.path.splitext(file)[0]
                )
                return html

    def update_tags(self, tag, post_id):
        # 更新标签，如果标签不存在就新创建一个标签并添加文章的id，如果存在就将文章id添加到已将存在的tag中

        tags = [t['tag'] for t in self._tags]
        for i in tag:
            if i not in tags:
                group = {}
                group['tag'] = i
                group['post_id'] = [post_id]
                self._tags.append(group)
            elif i in tags:
                index = tags.index(i)
                self._tags[index]['post_id'].append(post_id)
        self.render_tag_html()

    def update_categories(self, category, post_id):

        categories = [t['category'] for t in self._categories]

        if category not in categories:
            group = {}
            group['category'] = category
            group['post_id'] = [post_id]
            self._categories.append(group)
        elif category in categories:
            index = categories.index(category)
            self._categories[index]['post_id'].append(post_id)

        self.render_cate_html()

    def render_index_html(self):
        """
        渲染首页
        :return:
        """
        template = self.env.get_template('index.html')  # 获取index的html页面并且传入参量
        html = template.render(
            posts=self._posts,
            title='首页',
            header_title=SITE_TITLE,
            header_subtitle=SITE_SUBTITLE
        )
        self.save_html('index.html', html, 'page')

    def render_tag_html(self):
        """
        渲染 tags 标签页面，就是包含了多少个标签
        :return:
        """
        template = self.env.get_template('tags.html')  # 获取tags.html页面
        tags = [t['tag'] for t in self._tags]
        counts = [len(t['post_id']) for t in self._tags]
        data = []
        for t, c in zip(tags, counts):  # 将两个list装换为元组的对象
            dict = {
                'tag': t,
                'count': c * 10 + 100
            }
            data.append(dict)
        html = template.render(
            data=data,
            title='标签'
        )
        self.save_html('tags.html', html, 'page')

    def render_cate_html(self):
        """
        渲染 categories 页面
        :return:
        """
        template = self.env.get_template('categories.html')
        cates = [c['category'] for c in self._categories]
        html = template.render(
            categories=cates,
            title='分类'
        )
        self.save_html('categories.html', html, 'page')

    def render_tag_posts(self, tag):  # 判断标签是不是在文章的标签列表里，如果在，那么文章就是该标签的文章，将他放入tag_post列表，并且渲染页面
        """
        渲染一个标签所有文章页，就是一个标签下拥有的文章
        :return:
        """
        tag_posts = []
        for p in self._posts:
            for t in tag:
                if t in p.get('tag'):
                    tag_posts.append(p)
                    template = self.env.get_template('tag.html')
                    html = template.render(
                        posts=tag_posts,
                        tag=t,
                        title='标签: ' + t
                    )
                    filename = t + '.html'
                    self.save_html(filename, html, 'page', extra_path='tag')
                tag_posts = []

    def render_cate_posts(self, category):
        """
        渲染一个分类所有文章，就是一个分类下的文章
        :param category:
        :return:
        """
        cate_posts = []
        for p in self._posts:
            if p.get('category') == category:
                cate_posts.append(p)

        template = self.env.get_template('category.html')
        html = template.render(
            posts=cate_posts,
            category=category,
            title='分类: ' + category
        )
        filename = category + '.html'
        self.save_html(filename, html, 'page', extra_path='category')

    def parse_meta(self, file, meta):
        """
        解析 meta 获得文章信息，因为可能没有meta属性，需要我们设置默认的meta
        :param file: xxx.md
        :param meta:
        :return:
        """
        # 默认今天日期
        now = datetime.now().strftime('%Y-%m-%d')
        date = meta.get('datetime')[0] if meta.get('datetime') else now
        tag = meta.get('tag', DEFAULT_TAG)
        category = meta.get('category')[0] if meta.get('category') else DEFAULT_CATEGORY
        title = meta.get('title')[0] if meta.get('title') else os.path.splitext(os.path.basename(file))[0]
        summary = meta.get('summary')[0] if meta.get('summary') else '无描述'
        url = meta.get('url')[0] if meta.get('url') else str(self.default_adder_id) + '.html'
        id = self.default_adder_id

        self.update_tags(tag, id)
        self.update_categories(category, id)
        data = {
            'datetime': date,
            'tag': tag,
            'category': category,
            'title': title,
            'summary': summary,
            'url': url,
            'id': id
        }
        return data

    def save_post_path(self, file, html):
        """
        根据文章meta中的日期，生成年份，月分来生成必要的信息提供给save_html函数（因为要创建对应的文件夹）
        :param file:
        :return:
        """
        filename = os.path.splitext(file)[0] + '.html'
        names = [t['filename'] for t in self._posts]

        if filename in names:
            index = names.index(filename)
            date = self._posts[index].get('datetime')
            year, month, _ = map(str, date.split('-'))
            self.save_html(file, html, 'post', year, month)

    def generate_post(self):
        """
        初始化时生成所有文章
        :return:
        """
        for file in self.load_folder(self._post_folder):
            html = self.markdown_to_html(file, 'post')
            self.save_post_path(os.path.basename(file), html)

    def generate_page(self):
        """
        初始化时生成所有页面
        :return:
        """
        for file in self.load_folder(self._page_folder):
            html = self.markdown_to_html(file, 'page')
            self.save_html(os.path.basename(file), html, 'page')

    def main(self):
        # 初始化时生成文章和页面，并进行存储
        self.generate_post()
        self.generate_page()
        self.dump_data()

    def __call__(self):
        self.main()
