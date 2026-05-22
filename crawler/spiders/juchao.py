import json
import scrapy
from datetime import datetime
from crawler.dedup import compute_simhash


JUCHAO_API = "http://www.cninfo.com.cn/new/disclosure"


def _get_column(code: str) -> str:
    """Map stock code prefix to Juchao disclosure column."""
    if code.startswith("300"):
        return "szse_gem"
    if code.startswith("002"):
        return "szse_sme"
    if code.startswith("000"):
        return "szse_main"
    if code.startswith("688"):
        return "kcb"
    return "shmb"


class JuchaoSpider(scrapy.Spider):
    name = "juchao"

    def start_requests(self):
        codes = self._get_chuanyu_codes()
        for code in codes:
            column = _get_column(code)
            params = {
                "column": column,
                "stock": code,
                "pageNum": "1",
                "pageSize": "10",
                "sortName": "noticeDate",
                "sortType": "desc",
            }
            url = f"{JUCHAO_API}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            yield scrapy.Request(
                url,
                callback=self.parse_disclosure,
                meta={"code": code},
                headers={"Referer": "http://www.cninfo.com.cn/"},
            )

    def _get_chuanyu_codes(self) -> list[str]:
        from crawler.spiders.eastmoney import EastmoneySpider
        spider = EastmoneySpider()
        codes = spider._get_sichuan_chongqing_codes()
        spider.client.close()
        return codes

    def parse_disclosure(self, response):
        code = response.meta["code"]
        try:
            data = json.loads(response.text)
            items = data.get("classifiedAnnouncements", []) or data.get("announcements", [])
        except json.JSONDecodeError:
            self.logger.error(f"JSON decode error for code {code}")
            return

        for item in items:
            title = item.get("announcementTitle", "")
            url_path = item.get("adjunctUrl", "")
            url = f"http://www.cninfo.com.cn/{url_path}" if url_path else ""
            publish_time_str = item.get("announcementTime", "")
            try:
                publish_time = datetime.fromtimestamp(int(publish_time_str) / 1000)
            except (ValueError, TypeError):
                continue

            if not title:
                continue

            yield {
                "code": code,
                "title": title.strip(),
                "content": "",
                "url": url,
                "source": "巨潮资讯",
                "publish_time": publish_time.isoformat(),
                "crawl_time": datetime.now().isoformat(),
                "simhash": compute_simhash(title, ""),
            }

