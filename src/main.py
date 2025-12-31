# src/main.py
import argparse
# ... 其他import

def main():
  parser = argparse.ArgumentParser(description="信息抽取实验系统")
  subparsers = parser.add_subparsers(dest='command')

  # 其他子命令...

  # 爬虫命令
  crawl_parser = subparsers.add_parser('crawl', help='爬取羽毛球新闻')
  crawl_parser.add_argument('--num', type=int, default=100, help='采集新闻数量')
  crawl_parser.add_argument('--save_dir', type=str, default='data/raw/', help='保存目录')
  # 信息抽取命令
  extract_parser = subparsers.add_parser('extract', help='正则表达式抽取比赛信息')
  extract_parser.add_argument('--input_dir', type=str, default='data/raw/', help='新闻稿目录')
  extract_parser.add_argument('--output', type=str, default='results/extracted.json', help='输出json路径')
  # 人工评价命令
  eval_parser = subparsers.add_parser('evaluate', help='人工评价抽取结果')
  eval_parser.add_argument('--extracted', type=str, default='results/extracted.json', help='抽取结果json')
  eval_parser.add_argument('--output', type=str, default='results/evaluation.json', help='人工评价结果json')
  eval_parser.add_argument('--stats', action='store_true', help='只显示统计信息')

  args = parser.parse_args()

  if args.command == 'crawl':
    from crawler import main as crawl_main
    crawl_main(num=args.num, save_dir=args.save_dir)
  elif args.command == 'extract':
    from extractor_regex import extract_from_dir
    extract_from_dir(args.input_dir, args.output)
  elif args.command == 'evaluate':
    from evaluation import evaluate_interactive, evaluation_stats
    if args.stats:
      evaluation_stats(args.output)
    else:
      evaluate_interactive(args.extracted, args.output)
  # ... 其他命令分支

if __name__ == "__main__":
  main()