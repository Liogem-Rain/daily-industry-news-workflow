# 每日行业新闻爬取工作流 (News Crawler Workflow)

这是一个用于每天自动抓取各大行业一线新闻的工具。它能够从配置的源（RSS Feed 或 网页）中提取新闻，并生成 Markdown 格式的日报。

## 功能特点
- **多行业支持**：涵盖科技、金融、医疗、能源等主流行业。
- **模块化设计**：支持通过 `config.yaml` 轻松添加新的新闻源。
- **自动调度**：内置定时任务功能，也可以配合系统 Cron 使用。
- **RSS优先**：利用 RSS 协议获取高质量、无广告的纯净内容。

## 快速开始

### 1. 安装依赖
确保你已经安装了 Python 3.8+。
```bash
pip install -r requirements.txt
```

### 2. 配置新闻源
编辑 `config.yaml` 文件，在 `sources` 列表中添加你想关注的 RSS 地址或网站。
```yaml
sources:
  - name: "TechCrunch"
    type: "rss"
    url: "https://techcrunch.com/feed/"
    category: "Technology"
    # ... 更多源
```

### 3. 运行爬虫
直接运行主程序：
```bash
python -m src.main
```
程序启动后会立即执行一次爬取任务，并生成 `daily_news_report.md` 文件。
之后，程序会进入后台运行模式，每天早上 **08:00** 自动执行一次。

## 高级用法

### 使用 GitHub Actions 实现全自动 (推荐)
如果你不想在本地一直运行电脑，可以将本项目上传到 GitHub，并配置 Actions。
1. 创建 `.github/workflows/daily_news.yml`
2. 配置定时任务 (Cron) 每天自动运行并提交生成的报告到仓库，或者发送邮件。

### 自定义爬虫逻辑
如果你需要爬取不支持 RSS 的网站，可以在 `src/crawlers/` 下继承 `BaseCrawler` 实现自定义解析逻辑。
```python
class MyCustomCrawler(BaseCrawler):
    def fetch_articles(self):
        soup = self.get_soup()
        # 使用 BeautifulSoup 解析页面...
```

## 输出示例
查看生成的 `daily_news_report.md` 获取最新资讯。
