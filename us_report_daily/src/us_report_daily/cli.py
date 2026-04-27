import argparse
import os
from .report_generator import generate_report

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("us_report_daily")
    p.add_argument("--excel", required=True, help="Path to Excel (xlsx/xlsm). Must contain cached calculated values.")
    p.add_argument("--asof", required=True, help="YYYYMMDD (e.g. 20260220)")
    p.add_argument("--gap", type=int, default=0, help="T-1 gap based on available dates (0 normal, 2 weekend etc)")
    p.add_argument("--content", default=os.path.join("content", "content.json"))
    p.add_argument("--template", default=os.path.join("templates", "template.html"))
    p.add_argument("--out", default=None, help="Output html path. default: output/report_YYYYMMDD.html")
    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    out = args.out or os.path.join("output", f"report_{args.asof}.html")

    path = generate_report(
        excel_path=args.excel,
        asof_str=args.asof,
        gap=args.gap,
        content_path=args.content,
        template_path=args.template,
        output_path=out,
    )
    print("[DONE] html:", path)
    return 0