from pathlib import Path
import os
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from dotenv import load_dotenv
from llm.prompt import load_prompt
from llm.llm_client import call_llm
import json

load_dotenv()
output_dir = Path(os.getenv("DATA_OUTPUT_PATH", "data/processed"))
output_dir.mkdir(parents=True, exist_ok=True)

def generate_data(schema_type: str):
    # Load content form file json llm/templates/system_prompt 
    system_prompt = load_prompt(f"system_{schema_type}.txt")

    # Gọi LLM
    response = call_llm(system_prompt)

    # store output from LLM to file .json 
    out_file = output_dir / f"{schema_type}_raw_llm_output.json"
    out_file.write_text(response, encoding="utf-8")
    print(f"[✓] Đã lưu LLM output cho {schema_type} → {out_file}")

if __name__ == "__main__":
    generate_data("acmbalance")
    generate_data("balance")
    generate_data("product")
    generate_data("subscriber")
    
