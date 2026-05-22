import scrapy
import httpx
from datetime import datetime
from lxml import html


POLICY_SOURCES = [
    {
        "name": "四川省人民政府",
        "url": "https://www.sc.gov.cn/10462/10778/10876/",
        "region": "四川",
        "xpath_title": '//ul[@class="list"]/li/a/text()',
        "xpath_link": '//ul[@class="list"]/li/a/@href',
        "xpath_date": '//ul[@class="list"]/li/span/text()',
    },
    {
        "name": "重庆市人民政府",
        "url": "https://www.cq.gov.cn/zwgk/zfxxgkzl/",
        "region": "重庆",
        "xpath_title": '//li/a/@title',
        "xpath_link": '//li/a/@href',
        "xpath_date": '//li/span/text()',
    },
]

INDUSTRY_KEYWORDS = {
    "白酒": ["白酒", "酿酒", "酒业"],
    "新能源": ["新能源", "光伏", "风电", "锂电", "储能"],
    "军工": ["军工", "国防", "航空航天"],
    "医药": ["医药", "生物", "医疗器械"],
    "房地产": ["房地产", "住房", "楼市"],
    "金融": ["金融", "银行", "证券", "保险"],
    "汽车": ["汽车", "新能源车", "智能网联"],
    "电子信息": ["电子信息", "半导体", "芯片", "软件"],
    "农业": ["农业", "农产品", "粮食"],
    "环保": ["环保", "碳中和", "节能减排"],
}


class PolicySpider(scrapy.Spider):
    name = "policy"

    def start_requests(self):
        for src in POLICY_SOURCES:
            yield scrapy.Request(
                src["url"],
                callback=self.parse_list,
                meta={"source": src},
                headers={"User-Agent": "Mozilla/5.0"},
            )

    def parse_list(self, response):
        src = response.meta["source"]
        tree = html.fromstring(response.text)
        titles = tree.xpath(src["xpath_title"])
        links = tree.xpath(src["xpath_link"])
        dates = tree.xpath(src["xpath_date"])

        for i in range(min(len(titles), len(links), len(dates))):
            title = titles[i].strip() if isinstance(titles[i], str) else str(titles[i])
            link = links[i]
            date_str = dates[i].strip() if isinstance(dates[i], str) else str(dates[i])

            if not link.startswith("http"):
                base = "/".join(src["url"].split("/")[:3])
                link = base + link if link.startswith("/") else src["url"] + link

            yield scrapy.Request(
                link,
                callback=self.parse_detail,
                meta={
                    "title": title,
                    "source_name": src["name"],
                    "region": src["region"],
                    "date_str": date_str,
                    "url": link,
                },
                headers={"User-Agent": "Mozilla/5.0"},
            )

    def parse_detail(self, response):
        title = response.meta["title"]
        content = " ".join(response.xpath("//div[contains(@class, 'content')]//text()").getall())
        content = content.strip()[:5000]
        date_str = response.meta.get("date_str", "")

        publish_time = datetime.now()
        for fmt in ["%Y-%m-%d", "%Y年%m月%d日", "%m-%d"]:
            try:
                publish_time = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue

        tags = []
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            if any(kw in title + content for kw in keywords):
                tags.append(industry)

        category = self._classify(title, content)

        yield {
            "title": title,
            "content": content,
            "source_url": response.meta["url"],
            "source_name": response.meta["source_name"],
            "publish_time": publish_time.isoformat(),
            "region": response.meta["region"],
            "category": category,
            "industry_tags": tags,
        }

    def _classify(self, title: str, content: str) -> str:
        text = title + content[:1000]
        if any(kw in text for kw in ["产业", "工业", "制造业"]):
            return "产业"
        if any(kw in text for kw in ["金融", "银行", "证券", "保险", "上市"]):
            return "金融"
        if any(kw in text for kw in ["税", "税收", "减免"]):
            return "税收"
        if any(kw in text for kw in ["土地", "用地", "征收"]):
            return "土地"
        if any(kw in text for kw in ["环保", "环境", "排放", "碳中和"]):
            return "环保"
        return "其他"
