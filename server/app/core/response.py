"""统一接口返回结构。"""


def ok(data=None, msg="成功"):
    """返回成功结果。"""
    return {"code": 200, "msg": msg, "data": data}


def page_data(rows, total):
    """组装分页数据。"""
    return {"list": rows, "total": total}


def paginate(query, page: int, page_size: int):
    """按页码截取查询结果。"""
    page = 1 if page < 1 else page
    page_size = 10 if page_size < 1 or page_size > 100 else page_size
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, rows
