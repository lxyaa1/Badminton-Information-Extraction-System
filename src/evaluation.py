import json
import os

def load_extracted(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_evaluation(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def evaluate_interactive(extracted_path, eval_path):
    data = load_extracted(extracted_path)
    evaluated = []
    print("人工评价说明：输入 1=正确，0=错误，2=部分正确，q=退出")
    for idx, item in enumerate(data, 1):
        print(f"\n第{idx}条：")
        print(f"比赛名称: {item.get('tournament')}")
        print(f"时间: {item.get('date')}")
        print(f"地点: {item.get('location')}")
        print(f"项目: {item.get('event')}")
        print(f"胜者: {item.get('winner')}")
        print(f"败者: {item.get('loser')}")
        print(f"比分: {item.get('score')}")
        label = input("标注(1=正确, 0=错误, 2=部分正确, q=退出): ").strip()
        if label == 'q':
            break
        if label not in {'1', '0', '2'}:
            print("输入无效，请重新输入。")
            continue
        label_map = {'1': '正确', '0': '错误', '2': '部分正确'}
        comment = input("备注(可选): ").strip()
        item_eval = dict(item)
        item_eval['label'] = label_map[label]
        if comment:
            item_eval['comment'] = comment
        evaluated.append(item_eval)
        # 实时保存，防止中断丢失
        save_evaluation(evaluated, eval_path)
    print(f"\n已评价 {len(evaluated)} 条，结果已保存至 {eval_path}")

def evaluation_stats(eval_path):
    data = load_extracted(eval_path)
    total = len(data)
    correct = sum(1 for x in data if x.get('label') == '正确')
    partial = sum(1 for x in data if x.get('label') == '部分正确')
    wrong = sum(1 for x in data if x.get('label') == '错误')
    print(f"总数: {total}")
    print(f"正确: {correct} ({correct/total:.2%})")
    print(f"部分正确: {partial} ({partial/total:.2%})")
    print(f"错误: {wrong} ({wrong/total:.2%})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="人工评价信息抽取结果")
    parser.add_argument('--extracted', type=str, default='../results/extracted.json', help='抽取结果json')
    parser.add_argument('--output', type=str, default='../results/evaluation.json', help='人工评价结果json')
    parser.add_argument('--stats', action='store_true', help='只显示统计信息')
    args = parser.parse_args()
    if args.stats:
        evaluation_stats(args.output)
    else:
        evaluate_interactive(args.extracted, args.output)
