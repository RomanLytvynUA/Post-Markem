import argparse
import sys
from flymark import get_adjudicators, get_competitors, get_final_marks

# 1. Map the string command to the actual function
# This acts as both your "Supported Actions" list AND your dispatcher
ACTION_MAP = {
    'judges': get_adjudicators,
    'competitors': get_competitors,
    'fmarks': get_final_marks
}

SUPPORTED_PROTOCOLS = ['fm']

def main():
    parser = argparse.ArgumentParser(description="Parser CLI")
    
    parser.add_argument(
        "protocol", 
        choices=SUPPORTED_PROTOCOLS,
        help="The scoring protocol used (e.g., fm=FlyMark)"
    )
    
    parser.add_argument(
        "file", 
        help="Path to the HTML/PDF file"
    )
    
    parser.add_argument(
        "action", 
        choices=ACTION_MAP.keys(),
        help="The data extraction task to perform"
    )

    parser.add_argument(
        "--out", 
        help="Path to save the output (JSON/CSV)", 
        required=False
    )
    
    args = parser.parse_args()
    
    try:
        if args.protocol == 'fm':
            print(f"[*] Engaged FlyMark Protocol on {args.file}")
        
        target_func = ACTION_MAP[args.action]
        result = target_func(args.file)
        
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(str(result))
            print(f"[+] Saved results to {args.out}")
        else:
            print(result)

    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()