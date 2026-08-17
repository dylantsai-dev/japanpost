"""互相匹配的浏览器画像：UA / Client Hints / Accept 保持一致。"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    name: str
    user_agent: str
    sec_ch_ua: str | None
    sec_ch_ua_mobile: str | None
    sec_ch_ua_platform: str | None
    accept: str
    accept_language: str
    accept_encoding: str
    extra: dict[str, str]


_CHROME_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/avif,image/webp,image/apng,*/*;q=0.8,"
    "application/signed-exchange;v=b3;q=0.7"
)
_FIREFOX_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/avif,image/webp,*/*;q=0.8"
)
_SAFARI_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "*/*;q=0.8"
)

_LANGS = (
    "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "ja,en-US;q=0.9,en;q=0.8",
    "ja-JP,ja;q=0.9,en-US;q=0.7,en;q=0.6,zh-CN;q=0.5",
    "ja-JP,ja;q=0.8,en-US;q=0.6,en;q=0.4",
)


def _chrome(
    name: str,
    ua: str,
    brands: str,
    platform: str,
    extra: dict[str, str] | None = None,
) -> BrowserProfile:
    return BrowserProfile(
        name=name,
        user_agent=ua,
        sec_ch_ua=brands,
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform=f'"{platform}"',
        accept=_CHROME_ACCEPT,
        accept_language=random.choice(_LANGS),
        accept_encoding="gzip, deflate, br, zstd",
        extra=extra or {},
    )


def random_profile() -> BrowserProfile:
    chrome_ver = random.choice([124, 126, 128, 131, 136, 139])
    chrome_full = random.choice([0, 1, 2, 3])
    brands = (
        f'"Not;A=Brand";v="99", "Google Chrome";v="{chrome_ver}", '
        f'"Chromium";v="{chrome_ver}"'
    )
    win_ua = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver}.0.0.{chrome_full} Safari/537.36"
    )
    mac_ua = (
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver}.0.0.{chrome_full} Safari/537.36"
    )
    linux_ua = (
        f"Mozilla/5.0 (X11; Linux x86_64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_ver}.0.0.{chrome_full} Safari/537.36"
    )
    edge_ver = random.choice([124, 128, 131, 136])
    edge_brands = (
        f'"Not;A=Brand";v="99", "Microsoft Edge";v="{edge_ver}", '
        f'"Chromium";v="{edge_ver}"'
    )
    edge_ua = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{edge_ver}.0.0.0 Safari/537.36 Edg/{edge_ver}.0.0.0"
    )
    ff_ver = random.choice([128, 131, 139, 141])
    ff_win = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{ff_ver}.0) "
        f"Gecko/20100101 Firefox/{ff_ver}.0"
    )
    ff_mac = (
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{ff_ver}.0) "
        f"Gecko/20100101 Firefox/{ff_ver}.0"
    )
    safari_ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
    )

    viewport = str(random.choice([1280, 1366, 1440, 1536, 1920, 2560]))
    dpr = random.choice(["1", "1.25", "1.5", "2"])

    chrome_extra = {
        "Sec-CH-UA-Full-Version-List": (
            f'"Not;A=Brand";v="10.0.1.4", "Google Chrome";v="{chrome_ver}.0.0.{chrome_full}", '
            f'"Chromium";v="{chrome_ver}.0.0.{chrome_full}"'
        ),
        "Sec-CH-Viewport-Width": viewport,
        "Sec-CH-DPR": dpr,
        "Sec-CH-UA-Platform-Version": random.choice(
            ['"15.0.0"', '"13.0.0"', '"10.0.0"', '"14.0.0"']
        ),
    }

    profiles = [
        _chrome("chrome-win", win_ua, brands, "Windows", chrome_extra),
        _chrome("chrome-mac", mac_ua, brands, "macOS", chrome_extra),
        _chrome("chrome-linux", linux_ua, brands, "Linux", chrome_extra),
        _chrome(
            "edge-win",
            edge_ua,
            edge_brands,
            "Windows",
            {
                "Sec-CH-Viewport-Width": viewport,
                "Sec-CH-DPR": dpr,
            },
        ),
        BrowserProfile(
            name="firefox-win",
            user_agent=ff_win,
            sec_ch_ua=None,
            sec_ch_ua_mobile=None,
            sec_ch_ua_platform=None,
            accept=_FIREFOX_ACCEPT,
            accept_language=random.choice(_LANGS),
            accept_encoding="gzip, deflate, br, zstd",
            extra={"TE": "trailers"},
        ),
        BrowserProfile(
            name="firefox-mac",
            user_agent=ff_mac,
            sec_ch_ua=None,
            sec_ch_ua_mobile=None,
            sec_ch_ua_platform=None,
            accept=_FIREFOX_ACCEPT,
            accept_language=random.choice(_LANGS),
            accept_encoding="gzip, deflate, br, zstd",
            extra={"TE": "trailers"},
        ),
        BrowserProfile(
            name="safari-mac",
            user_agent=safari_ua,
            sec_ch_ua=None,
            sec_ch_ua_mobile=None,
            sec_ch_ua_platform=None,
            accept=_SAFARI_ACCEPT,
            accept_language=random.choice(_LANGS),
            accept_encoding="gzip, deflate, br",
            extra={},
        ),
    ]
    return random.choice(profiles)


def headers_for(
    profile: BrowserProfile,
    *,
    referer: str | None,
    navigate: bool = True,
    same_origin: bool = True,
) -> dict[str, str]:
    headers: dict[str, str] = {
        "User-Agent": profile.user_agent,
        "Accept": profile.accept,
        "Accept-Language": profile.accept_language,
        "Accept-Encoding": profile.accept_encoding,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": random.choice(["max-age=0", "no-cache"]),
        "Pragma": "no-cache",
        "DNT": random.choice(["1", "1"]),
    }
    if random.random() < 0.7:
        headers["Sec-GPC"] = "1"

    if profile.sec_ch_ua:
        headers["Sec-CH-UA"] = profile.sec_ch_ua
        headers["Sec-CH-UA-Mobile"] = profile.sec_ch_ua_mobile or "?0"
        headers["Sec-CH-UA-Platform"] = profile.sec_ch_ua_platform or '"Windows"'
        headers.update(profile.extra)
        headers["Sec-Fetch-Dest"] = "document" if navigate else "empty"
        headers["Sec-Fetch-Mode"] = "navigate" if navigate else "cors"
        headers["Sec-Fetch-Site"] = (
            "same-origin" if same_origin else ("same-site" if referer else "none")
        )
        if navigate:
            headers["Sec-Fetch-User"] = "?1"
    else:
        headers.update(profile.extra)

    if referer:
        headers["Referer"] = referer

    # 少量请求带 Priority（Chrome）
    if profile.sec_ch_ua and random.random() < 0.8:
        headers["Priority"] = "u=0, i"

    return headers
