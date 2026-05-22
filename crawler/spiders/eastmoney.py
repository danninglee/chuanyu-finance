import json
import scrapy
import httpx
from datetime import datetime
from crawler.dedup import compute_simhash


EASTMONEY_LIST_API = "https://push2.eastmoney.com/api/qt/clist/get"


class EastmoneySpider(scrapy.Spider):
    name = "eastmoney"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.Client(timeout=30)

    def start_requests(self):
        codes = self._get_sichuan_chongqing_codes()
        for code in codes:
            market_code = self._add_market_prefix(code)
            url = (
                f"https://np-anotice-stock.eastmoney.com/api/security/ann?"
                f"stock_list={market_code}&page_size=20&page_index=1"
            )
            yield scrapy.Request(
                url,
                callback=self.parse_news,
                meta={"code": code},
                headers={"Referer": "https://guba.eastmoney.com/"},
            )

    @staticmethod
    def _add_market_prefix(code: str) -> str:
        """Eastmoney API requires market prefix: 0 for SZ, 1 for SH."""
        if code.startswith(("0", "3")):
            return f"0.{code}"
        if code.startswith("6"):
            return f"1.{code}"
        return code

    def _get_sichuan_chongqing_codes(self) -> list[str]:
        """Fetch stock codes for Sichuan and Chongqing boards."""
        codes = []
        for bk_code in ["BK0169", "BK0170"]:
            params = {
                "pn": "1",
                "pz": "300",
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": f"b:{bk_code}+f:!200",
                "fields": "f12",
            }
            try:
                resp = self.client.get(EASTMONEY_LIST_API, params=params)
                data = resp.json()
                if data.get("data") and data["data"].get("diff"):
                    for item in data["data"]["diff"]:
                        code = item.get("f12", "")
                        if code and (code.startswith(("0", "3", "6"))):
                            codes.append(code)
            except Exception as e:
                self.logger.error(f"Failed to fetch codes for {bk_code}: {e}")
        return list(set(codes))

    def parse_news(self, response):
        code = response.meta["code"]
        try:
            data = json.loads(response.text)
            items = data.get("data", {}).get("list", [])
        except json.JSONDecodeError:
            self.logger.error(f"JSON decode error for code {code}")
            return

        for item in items:
            title = item.get("art_title", "")
            content = item.get("content", "")
            url = item.get("art_code", "")
            if url and not url.startswith("http"):
                url = f"https://np-anotice-stock.eastmoney.com/detail/{url}"
            publish_time_str = item.get("notice_date", "")
            try:
                publish_time = datetime.strptime(publish_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            if not title:
                continue

            yield {
                "code": code,
                "title": title.strip(),
                "content": content.strip() if content else "",
                "url": url,
                "source": "东方财富",
                "publish_time": publish_time.isoformat(),
                "crawl_time": datetime.now().isoformat(),
                "simhash": compute_simhash(title, content or ""),
            }

    def closed(self, reason):
        self.client.close()
