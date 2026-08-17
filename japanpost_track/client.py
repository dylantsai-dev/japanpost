from __future__ import annotations

import random
import time
from typing import Any
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

from .browsers import BrowserProfile, headers_for, random_profile

ORIGIN = "https://trackings.post.japanpost.jp"
HOME = "https://www.post.japanpost.jp/"
SEARCH = f"{ORIGIN}/services/srv/search/"
DIRECT = f"{ORIGIN}/services/srv/search/direct"


class TrackingError(RuntimeError):
    pass


def _sleep() -> None:
    time.sleep(random.uniform(0.35, 1.25))


def _session(profile: BrowserProfile) -> requests.Session:
    s = requests.Session()
    s.headers.update(headers_for(profile, referer=None, navigate=True, same_origin=False))
    adapter = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=0)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


def _get(
    session: requests.Session,
    profile: BrowserProfile,
    url: str,
    *,
    params: dict[str, str] | None = None,
    referer: str | None,
    same_origin: bool,
) -> requests.Response:
    headers = headers_for(
        profile,
        referer=referer,
        navigate=True,
        same_origin=same_origin,
    )
    # GET 导航一般不带 Origin；防盗链靠 Referer + Cookie。
    resp = session.get(
        url,
        params=params,
        headers=headers,
        timeout=25,
        allow_redirects=True,
    )
    resp.raise_for_status()
    return resp


def _warmup(session: requests.Session, profile: BrowserProfile) -> str:
    """先打日本郵便主站 / 查询页，拿 Cookie，后续带 Referer 再查单号。"""
    _get(
        session,
        profile,
        HOME,
        referer=None,
        same_origin=False,
    )
    _sleep()
    search_url = f"{SEARCH}?locale=ja"
    _get(
        session,
        profile,
        search_url,
        referer=HOME,
        same_origin=False,
    )
    return search_url


def _parse(html: str, tracking_no: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("h1")
    product = ""
    if title:
        text = title.get_text(" ", strip=True)
        if "[" in text and "]" in text:
            product = text[text.find("[") + 1 : text.find("]")]

    detail: dict[str, str] = {}
    table = soup.find("table", attrs={"summary": "配達状況詳細"})
    if table:
        rows = table.find_all("tr")
        headers: list[str] = []
        for i, tr in enumerate(rows):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if i == 0:
                headers = cells
                continue
            if headers and len(cells) == len(headers) and i == 1:
                detail.update({k: v for k, v in zip(headers, cells) if k})
                headers = []
                continue
            # 后续区块：先 th 行再 td 行
            if all(tr.find_all("th")) and not tr.find_all("td"):
                headers = cells
            elif headers:
                detail.update({k: v for k, v in zip(headers, cells) if k})
                headers = []

    events: list[dict[str, str]] = []
    hist = soup.find("table", attrs={"summary": "履歴情報"})
    if hist:
        pending: dict[str, str] | None = None
        for tr in hist.find_all("tr"):
            tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if not tds:
                continue
            if len(tds) >= 4 and tds[0]:
                pending = {
                    "time": tds[0],
                    "status": tds[1],
                    "detail": tds[2] if len(tds) > 2 else "",
                    "office": tds[3] if len(tds) > 3 else "",
                    "prefecture": tds[4] if len(tds) > 4 else "",
                    "zip": "",
                }
                events.append(pending)
            elif pending and len(tds) == 1 and tds[0]:
                pending["zip"] = tds[0]

    if not events and "該当するデータがありません" in html:
        raise TrackingError(f"单号 {tracking_no} 无轨迹数据")

    return {
        "tracking_no": tracking_no,
        "product": product,
        "detail": detail,
        "events": events,
    }


def track(tracking_no: str, *, search_kind: str = "S002") -> dict[str, Any]:
    no = tracking_no.replace("-", "").replace(" ", "").strip()
    if not no:
        raise TrackingError("单号为空")

    profile = random_profile()
    session = _session(profile)
    search_referer = _warmup(session, profile)
    _sleep()

    params = {
        "reqCodeNo1": no,
        "searchKind": search_kind,
        "locale": "ja",
    }
    resp = _get(
        session,
        profile,
        DIRECT,
        params=params,
        referer=search_referer,
        same_origin=True,
    )
    result = _parse(resp.text, no)
    result["_meta"] = {
        "browser": profile.name,
        "user_agent": profile.user_agent,
        "status_code": resp.status_code,
        "final_url": resp.url,
        "cookies": {k: v for k, v in session.cookies.items()},
        "query": f"{DIRECT}?{urlencode(params)}",
    }
    return result
