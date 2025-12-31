# src/crawler.py
import os
import time
import argparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

BASE_URL = "https://www.badmintoncn.com/"
LIST_URL = "https://www.badmintoncn.com/list.php?tid=2&page={}"  # 赛事频道分页

# 使用验证过的完整headers
headers = {
    'authority': 'www.badmintoncn.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'cookie': 'cbo_click_cookie_09521f0dad7121889e6fe5c11a782319=1751169982; rcKA_379b_saltkey=fZ36VV33; rcKA_379b_lastvisit=1751166470; cbo_click_cookie_8602166a039111de8b3a2e6de9e8c9c1=1751170098; rcKA_379b_connect_is_bind=0; rcKA_379b_visitedfid=81; rcKA_379b_smile=1D1; userLoginJudge2187073=y; Hm_lvt_cfc948fc40dd345b6e12298c5c40ba13=1751169795,1751274706; HMACCOUNT=9A6A3D9427EE0E80; setHits9748=y; setHits14147=y; cbo_click_cookie_0eaa5c08d3416d28dae9163ce89de765=1751276048; rcKA_379b_sendmail=1; rcKA_379b_seccode=1546.4d69f325584380c931; rcKA_379b_ulastactivity=1751276244|0; rcKA_379b_auth=394blhxoLo3VnQlRpHgESar6TjgXNG/UKnM8fqQYm/vwxJeIxHltop17PHeWOLYCwTvoHT8EIudhnygPZNN+v1CIkZwg; rcKA_379b_myrepeat_rr=R0; cbo_auth=694307ye3J6FPNIbUOOMC7lIW0iykC2qu3PT9swnujVQ9PyFrCgyQRwgg2vniaM; oms_auth=d9039bZx3EDWlhrnNxgf8SlmRzeM7Kb0oVOBWk/+FGaj82y+mIDWlZv5wUe8PY48; rcKA_379b_lastact=1751276248|09portal.php|09; setHits6652=y; Hm_lpvt_cfc948fc40dd345b6e12298c5c40ba13=1751276266',
    'priority': 'u=0, i',
    'referer': 'https://www.badmintoncn.com/list.php?tid=2',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'
}

# 创建会话对象，共享headers和cookies
session = requests.Session()
session.headers.update(headers)

def fetch_badmintoncn_news_urls(pages=10):
    """
    获取中羽在线赛事新闻的新闻链接
    """
    url_list = []
    for i in range(1, pages + 1):
        url = LIST_URL.format(i)
        try:
            print(f"正在抓取第{i}页: {url}")
            
            # 使用会话对象发送请求
            resp = session.get(url, timeout=15)
            print(f"HTTP状态码: {resp.status_code}")
            
            if resp.status_code != 200:
                # 保存错误页面用于调试
                with open(f"error_page_{i}.html", "w", encoding="gbk") as f:
                    f.write(resp.text)
                print(f"页面获取失败: {url}")
                continue
                
            # 使用正确的编码
            resp.encoding = 'gbk'  # 网站实际使用的编码
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 改进选择器 - 更符合实际结构
            list_box = soup.select_one('div.listbox')
            if list_box:
                news_items = list_box.select('li')
            else:
                print("未找到listbox容器")
                continue
                
            found_count = 0
            for li in news_items:
                # 改进提取方式：优先获取class="newstitle"的链接
                news_title = li.find('a', class_='newstitle')
                
                # 如果没有找到，尝试其他方式
                if not news_title:
                    # 在li内部查找包含news.php?id=的链接
                    links = li.find_all('a', href=re.compile(r'news\.php\?id=\d+'))
                    if links:
                        # 取第一个链接作为新闻标题链接
                        news_title = links[0]
                
                if news_title and 'href' in news_title.attrs:
                    href = news_title['href']
                    title = news_title.get_text(strip=True)
                    
                    # 放宽过滤条件
                    if any(char in title for char in ['｜', '|']):
                        # 处理相对URL
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                news_url = BASE_URL + href[1:]
                            else:
                                news_url = BASE_URL + href
                        else:
                            news_url = href
                            
                        print(f"发现匹配标题 [{title}] -> {news_url}")
                        url_list.append(news_url)
                        found_count += 1
            
            print(f"第{i}页找到{found_count}条新闻")
            time.sleep(1)  # 增加延迟避免被封
            
        except Exception as e:
            print(f"抓取列表页失败: {url}，原因: {str(e)[:200]}")
    
    return list(dict.fromkeys(url_list))

def fetch_article(url):
    """
    抓取单篇新闻正文
    """
    try:
        # 使用同一个会话对象发送请求
        resp = session.get(url, timeout=15)
        
        # 如果返回的是重定向或验证页面
        if "验证" in resp.text or "问题" in resp.text:
            print(f"访问文章页面时触发验证: {url}")
            return None
            
        # 使用正确的编码
        resp.encoding = 'gbk'
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 查找正文内容 - 实际查看页面发现是id="content"
        content_div = soup.find('div', id='content')
        
        if not content_div:
            print(f"未找到正文: {url}")
            return None
            
        # 提取纯文本
        text = content_div.get_text(separator='\n', strip=True)
        return text
        
    except Exception as e:
        print(f"抓取失败: {url}，原因: {e}")
        return None

def save_article(text, idx, save_dir):
    """
    保存新闻到本地txt文件
    """
    filename = os.path.join(save_dir, f"match_{idx:03d}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def main(num=100, save_dir="data/raw/"):
    os.makedirs(save_dir, exist_ok=True)
    print(f"开始爬取中羽在线赛事新闻，目标数量：{num}")
    
    # 计算需要的页数（每页大约15条新闻）
    pages = min(20, (num // 15) + 2)  # 设置上限为10页
    
    urls = fetch_badmintoncn_news_urls(pages=pages)
    print(f"共获取到{len(urls)}条新闻链接")
    
    if not urls:
        print("未获取到任何链接，程序终止")
        return
        
    count = 0
    for idx, url in enumerate(tqdm(urls, desc="采集新闻")):
        if count >= num:
            break
        text = fetch_article(url)
        if text and len(text) > 100:  # 过滤过短内容
            save_article(text, count + 1, save_dir)
            count += 1
        # 每处理一条新闻后稍作延迟
        time.sleep(0.5)
            
    print(f"实际采集到{count}篇新闻，已保存在 {save_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="中羽在线赛事新闻爬虫")
    parser.add_argument('--num', type=int, default=100, help='采集新闻数量')
    parser.add_argument('--save_dir', type=str, default='data/raw/', help='保存目录')
    args = parser.parse_args()
    main(num=args.num, save_dir=args.save_dir)