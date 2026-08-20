import json
import os
import pandas as pd
from glob import glob
from datetime import datetime

def compile_json_to_csv(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    base_dir = f"outputs/{date_str}"
    raw_dir = f"{base_dir}/raw"
    
    if not os.path.exists(raw_dir):
        print(f"Error: Directory {raw_dir} does not exist.")
        return

    all_features = []
    
    # Find all JSON files in the raw directory
    json_files = glob(os.path.join(raw_dir, "*.json"))
    
    for file_path in json_files:
        competitor_name = os.path.basename(file_path).replace(".json", "").capitalize()
        print(f"Processing {competitor_name}...")
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            features = data.get("all_features", [])
            for feat in features:
                feat_copy = feat.copy()
                feat_copy["competitor"] = competitor_name
                # Convert list of tiers to a comma-separated string
                if isinstance(feat_copy.get("available_in_tiers"), list):
                    feat_copy["available_in_tiers"] = ", ".join(feat_copy["available_in_tiers"])
                all_features.append(feat_copy)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if all_features:
        df = pd.DataFrame(all_features)
        # Reorder columns to put competitor first
        cols = ["competitor"] + [c for c in df.columns if c != "competitor"]
        df = df[cols]
        
        output_path = f"{base_dir}/compiled_features.csv"
        df.to_csv(output_path, index=False)
        print(f"\nSuccessfully compiled {len(all_features)} features into {output_path}")
    else:
        print("No features found to compile.")

if __name__ == "__main__":
    # You can specify a date here if needed, e.g., compile_json_to_csv("2026-01-03")
    compile_json_to_csv()

