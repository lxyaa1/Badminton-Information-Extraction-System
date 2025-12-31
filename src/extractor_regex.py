import os
import re
import json

def extract_match_info_from_text(content):
    """
    从单篇新闻稿中提取比赛信息
    返回包含以下信息的字典列表：
    - 比赛名称
    - 时间
    - 地点
    - 胜者
    - 败者
    - 比分
    - 项目（男单/女单/男双/女双/混双）
    """
    results = []
    
    # 1. 提取比赛名称（如"2025年美国羽毛球公开赛决赛"）
    tournament_pattern = r'(\d{4}年[\u4e00-\u9fa5]+羽毛球(?:公开赛|大师赛|.*赛)[^。，；：]*赛)'
    tournament_match = re.search(tournament_pattern, content)
    tournament_name = tournament_match.group(0) if tournament_match else "未知比赛"
    
    # 2. 提取日期（如"北京时间6月30日"）
    date_pattern = r'北京时间(\d{1,2}月\d{1,2}日)'
    date_match = re.search(date_pattern, content)
    date = date_match.group(1) if date_match else "未知日期"
    
    # 3. 从比赛名称中提取地点
    location_pattern = r'年([\u4e00-\u9fa5]+)羽毛球'
    location_match = re.search(location_pattern, tournament_name)
    location = location_match.group(1) if location_match else "未知地点"
    
    # 4. 分割文本为独立句子，提高匹配准确率
    sentences = [s.strip() for s in re.split(r'[。，；\n]', content) if len(s.strip()) > 5]
    
    # 5. 定义核心正则：匹配完整的比赛结果
    # 格式：[胜者信息][比分信息][胜负动词][败者信息]
    match_pattern = re.compile(
        r'([\u4e00-\u9fa5a-zA-Z\s\/]+?[^\d]+?)'  # 胜者（包含国家/组合信息）
        r'(?:以|)[\s]*([\d\s,-]{5,}?)[\s]*'      # 比分（允许"以"前缀）
        r'(?:直落|击败|战胜|赢下|逆转|轻取|力克|淘汰|不敌|胜|负|惜败)'  # 胜负动词
        r'[\s、，]*([\u4e00-\u9fa5a-zA-Z\s\/]+)' # 败者
    )
    
    # 6. 项目类型识别
    event_types = {"男单", "女单", "男双", "女双", "混双"}
    
    for sentence in sentences:
        # 先检查是否有项目类型
        current_event = None
        for event in event_types:
            if event in sentence:
                current_event = event
                break
        
        # 核心匹配：查找所有比赛结果
        matches = match_pattern.findall(sentence)
        for winner_info, score, loser_info in matches:
            # 清理空白字符
            winner = re.sub(r'\s{2,}', ' ', winner_info.strip())
            loser = re.sub(r'\s{2,}', ' ', loser_info.strip())
            score_clean = re.sub(r'\s', '', score.strip())
            
            # 规范化双打选手姓名格式
            winner = winner.replace(' ', '/').replace('//', '/')
            loser = loser.replace(' ', '/').replace('//', '/')
            
            results.append({
                "tournament": tournament_name,
                "date": date,
                "location": location,
                "event": current_event or "未知项目",
                "winner": winner,
                "loser": loser,
                "score": score_clean
            })
    
    return results

def extract_all_matches(raw_dir):
    """
    批量处理raw目录下的所有新闻稿
    返回包含所有比赛信息的列表
    """
    all_matches = []
    for filename in os.listdir(raw_dir):
        if filename.endswith('.txt'):
            path = os.path.join(raw_dir, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            all_matches.extend(extract_match_info_from_text(content))
    return all_matches

def save_results(data, output_path):
    """保存结果到JSON文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_from_dir(input_dir, output_path):
    """
    兼容 main.py 的调用方式，批量抽取并保存结果
    """
    matches = extract_all_matches(input_dir)
    save_results(matches, output_path)
    print(f"成功抽取 {len(matches)} 条比赛记录，保存至 {output_path}")

# 示例使用
if __name__ == "__main__":
    RAW_DIR = 'data/raw'  # 原始文本目录
    OUTPUT_PATH = 'results/extracted.json'  # 输出文件路径
    
    # 创建输出目录
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    # 提取并保存结果
    matches = extract_all_matches(RAW_DIR)
    save_results(matches, OUTPUT_PATH)
    print(f"成功抽取 {len(matches)} 条比赛记录，保存至 {OUTPUT_PATH}")