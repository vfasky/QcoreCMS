Qcore CMS v2
================

**愿景： 高性能、 高定制性、 高扩展性**

所有数据库查询, cache, session 均为异步

**注： 目前只是开发版， 进度 5%**

## 依赖库 

- tornado
- peewee
- Momoko
- Jinja2
- wtforms
- arrow

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

