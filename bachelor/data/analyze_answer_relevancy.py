import requests
import json
from collections import defaultdict, Counter

def fetch_data(url):
    """Fetch data from the API endpoint"""
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

def analyze_answer_relevancy_zeros(all_scores):
    """Analyze answer_relevancy scores and find indexes with 0.0 values"""
    all_zero_indexes = []  # List to store all zero indexes from all records
    record_zero_indexes = {}  # Dict to store zero indexes per record
    
    record_counter = 1
    
    for scores_entry in all_scores:
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

        if "answer_relevancy" not in scores_dict:
            print(f"⚠ Missing 'answer_relevancy' key in record {record_counter}")
            record_counter += 1
            continue

        # Find indexes where answer_relevancy is 0.0
        zero_indexes = [k for k, v in scores_dict["answer_relevancy"].items() if v == 0.0]
        
        if zero_indexes:
            record_zero_indexes[record_counter] = zero_indexes
            all_zero_indexes.extend(zero_indexes)
            print(f"Record {record_counter}: Zero indexes = {zero_indexes}")
        else:
            print(f"Record {record_counter}: No zero answer_relevancy scores")
        
        record_counter += 1
    
    return record_zero_indexes, all_zero_indexes

def find_overlapping_indexes(record_zero_indexes):
    """Find indexes that appear in multiple records"""
    index_counter = Counter()
    
    # Count occurrences of each index across all records
    for record_id, indexes in record_zero_indexes.items():
        for idx in indexes:
            index_counter[idx] += 1
    
    # Find indexes that appear in more than one record
    overlapping_indexes = {idx: count for idx, count in index_counter.items() if count > 1}
    
    return overlapping_indexes, index_counter

def main():
    url = "http://localhost:9876/ratings/?status=Completed&testset_id=38&llm_to_be_evaluated_type=openai/gpt-4.1&show_scores=True"
    
    print("Fetching data from API...")
    try:
        all_scores = fetch_data(url)
        print(f"✅ Successfully fetched {len(all_scores)} records")
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return
    
    print("\n" + "="*60)
    print("ANALYZING ANSWER_RELEVANCY ZEROS")
    print("="*60)
    
    record_zero_indexes, all_zero_indexes = analyze_answer_relevancy_zeros(all_scores)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print(f"Total records processed: {len(all_scores)}")
    print(f"Records with zero answer_relevancy scores: {len(record_zero_indexes)}")
    print(f"Total zero indexes found: {len(all_zero_indexes)}")
    print(f"Unique zero indexes: {len(set(all_zero_indexes))}")
    
    if record_zero_indexes:
        print(f"\nAll zero indexes: {sorted(set(all_zero_indexes))}")
        
        overlapping_indexes, index_counter = find_overlapping_indexes(record_zero_indexes)
        
        if overlapping_indexes:
            print(f"\nOVERLAPPING INDEXES (appear in multiple records):")
            print("-" * 50)
            for idx, count in sorted(overlapping_indexes.items()):
                print(f"Index '{idx}': appears in {count} records")
        else:
            print(f"\nNo overlapping indexes found - each zero index appears in only one record")
        
        print(f"\nDETAILED INDEX FREQUENCY:")
        print("-" * 30)
        for idx, count in sorted(index_counter.items()):
            print(f"Index '{idx}': {count} time(s)")
    else:
        print("No records found with zero answer_relevancy scores")

if __name__ == "__main__":
    main() 