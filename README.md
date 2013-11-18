Qcore CMS v2
================

**愿景： 高性能、 高定制性、 高扩展性**

所有数据库查询, cache, session 均为异步

**注： 目前只是开发版， 进度 7%**

## 依赖库 

- tornado
- peewee
- Momoko
- Jinja2
- wtforms
- arrow

## 前端

- [AngularJS v 1.5.1]([http://angularjs.org/)
- [Twitter Bootstrap v 3.0.2](http://getbootstrap.com/)

## 数据库

- postgresql

## 安装

```bash
pip install -r requirements.txt
```

## 运行

修改 `config.def.py` 的配置，并改名 `config.py`

```bash
python xcms.py --port=8080
```

