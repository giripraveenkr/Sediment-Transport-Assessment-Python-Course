import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# terrain_assessment.py
import argparse
from src.wrr.scripts.run_analysis import main as run_pipeline

def parse_args():
    parser = argparse.ArgumentParser(description="Run terrain assessment pipeline.")
    parser.add_argument(
        "--bbox",
        type=str,
        required=True,
        help="Bounding box as minx,miny,maxx,maxy"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    print("Running project with bbox:", args.bbox)
    run_pipeline(args.bbox)

if __name__ == "__main__":
    main()