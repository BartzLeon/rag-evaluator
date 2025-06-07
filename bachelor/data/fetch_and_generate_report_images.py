import requests
import json
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from tqdm import tqdm

plt.switch_backend('Agg')

ATTRIBUTES = ["answer_relevancy", "context_precision", "faithfulness", "context_recall"]

def fetch_data(testset_id):
    url = f"http://localhost:9876/ratings/?status=Completed&show_scores=True&testset_id={testset_id}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def clean_record(record):
    if "answer_relevancy" not in record:
        raise ValueError("Missing 'answer_relevancy' key.")

    #indices_to_remove = [k for k, v in record["answer_relevancy"].items() if v == 0.0]
    indices_to_remove = []

    for attribute in ATTRIBUTES:
        if attribute in record:
            for idx in indices_to_remove:
                record[attribute].pop(idx, None)
    return record

def process_and_plot(all_scores, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Create one PdfPages writer per attribute
    pdf_writers = {attr: PdfPages(os.path.join(output_dir, f"{attr}.pdf")) for attr in ATTRIBUTES}

    record_counter = 1

    for scores_entry in tqdm(all_scores, desc="Processing result objects"):
        scores_string = scores_entry.get("scores")
        if not scores_string:
            print(f"⚠ Skipping record {record_counter}: empty or missing 'scores'")
            record_counter += 1
            continue

        try:
            scores_dict = json.loads(scores_string)
        except json.JSONDecodeError as e:
            print(f"⚠ Failed to parse JSON for record {record_counter}: {e}")
            record_counter += 1
            continue

        try:
            cleaned_record = clean_record(scores_dict)
        except Exception as e:
            print(f"⚠ Skipping record {record_counter}: {e}")
            record_counter += 1
            continue

        for attr in ATTRIBUTES:
            if attr not in cleaned_record:
                print(f"⚠ Missing attribute {attr} in record {record_counter}")
                continue

            raw_values = cleaned_record[attr].values()
            values = [float(v) for v in raw_values if v is not None]

            if not values:
                print(f"⚠ No valid values found for {attr} in record {record_counter}")
                continue

            mean_val = np.mean(values)

            plt.figure(figsize=(8, 4))
            plt.hist(values, bins=10, color='skyblue', edgecolor='black')
            plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=1)
            plt.title(f"Record {record_counter}: {attr} (mean={mean_val:.2f})")
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.xlim(0, 1)
            plt.grid(True)

            pdf_writers[attr].savefig()
            plt.close()

        record_counter += 1

    # Close all pdf writers
    for writer in pdf_writers.values():
        writer.close()

    print(f"✅ Successfully processed {record_counter-1} records and generated 4 PDFs.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("testset_id", type=int, help="Testset ID to fetch")
    args = parser.parse_args()

    all_scores = fetch_data(args.testset_id)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f"./results/{timestamp}_testset_{args.testset_id}"
    process_and_plot(all_scores, output_dir)

    print(f"✅ All files saved in: {output_dir}")

if __name__ == "__main__":
    main()