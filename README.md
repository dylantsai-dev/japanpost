# japanpost-track

查询日本邮政（ゆうパック）物流轨迹。带随机浏览器请求头、Referer 链和 Session Cookie。

## 安装

```bash
uv pip install dist/japanpost_track-0.1.0-py3-none-any.whl
# 或从源码
uv pip install .
```

## 命令行

```bash
jp-track 955187518762
uv run python -m japanpost_track 955187518762
```

## Python

```python
from japanpost_track import track

result = track("955187518762")
print(result["events"])
```
