import argparse
import sys
import json
import pandas as pd
from flymark import get_adjudicators, get_competitors, get_final_marks

ACTION_MAP = {
    'judges': get_adjudicators,
    'competitors': get_competitors,
    'fmarks': get_final_marks
}

SUPPORTED_PROTOCOLS = ['fm']

def save_result(data, filepath):
    """Smart saver that handles both Dicts/Lists and Pandas DataFrames."""
    try:
        if isinstance(data, (pd.DataFrame, pd.Series)):
            data.to_json(filepath, orient='split', indent=4, force_ascii=False)
        elif isinstance(data, dict) and any(isinstance(v, (pd.DataFrame, pd.Series)) for v in data.values()):
             serializable_data = {
                 k: v.to_dict(orient='split') if isinstance(v, pd.DataFrame) else v 
                 for k, v in data.items()
             }
             with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=4, ensure_ascii=False)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
        print(f"[+] Saved results to {filepath}")
        
    except Exception as e:
        print(f"[!] Serialization Error: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Parser CLI")
    
    parser.add_argument("protocol", choices=SUPPORTED_PROTOCOLS, help="The scoring protocol used")
    parser.add_argument("file", help="Path to the HTML/PDF file")
    parser.add_argument("action", choices=ACTION_MAP.keys(), help="The extraction task")
    parser.add_argument("--out", help="Path to save the output (JSON)", required=False)
    
    args = parser.parse_args()
    
    try:
        if args.protocol == 'fm':
            print(f"[*] Engaged FlyMark Protocol on {args.file}")
        
        target_func = ACTION_MAP[args.action]
        result = target_func(args.file)
        
        if args.out:
            save_result(result, args.out)
        else:
            import pprint
            pprint.pprint(result)

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()