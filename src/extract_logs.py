import sys
import os

INDEX_FILE = "log_index.txt"
OUTPUT_DIR = "output"

def build_index(log_file):
    """
    Builds an index file containing byte offsets of each day's logs.
    """
    index = {}
    with open(log_file, "r", encoding="utf-8") as f:
        while True:
            pos = f.tell()  # Get current file position
            line = f.readline()
            if not line:
                break
            
            date = line[:10]  # Extract YYYY-MM-DD
            if date not in index:
                index[date] = pos  # Store the first occurrence of the date

    with open(INDEX_FILE, "w", encoding="utf-8") as f_idx:
        for date, offset in index.items():
            f_idx.write(f"{date} {offset}\n")

    print(f"Index built successfully in {INDEX_FILE}")

def load_index():
    """
    Loads the index file into a dictionary.
    """
    if not os.path.exists(INDEX_FILE):
        return None
    
    index = {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            date, offset = line.strip().split()
            index[date] = int(offset)
    return index

def extract_logs(log_file, date):
    """
    Extracts log entries for a given date using an index if available.
    Falls back to line-by-line search if the index does not exist.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_file = os.path.join(OUTPUT_DIR, f"output_{date}.txt")
    
    index = load_index()

    if index and date in index:
        # Use index-based retrieval
        with open(log_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
            f_in.seek(index[date])  # Jump to the offset

            for line in f_in:
                if not line.startswith(date):
                    break  # Stop reading when the date changes
                f_out.write(line)
        
        print(f"Logs for {date} saved to {output_file} (Using Index)")

    else:
        # Fallback to line-by-line streaming
        print("Index not found. Using slower line-by-line search...")
        with open(log_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
            for line in f_in:
                if line.startswith(date):
                    f_out.write(line)

        print(f"Logs for {date} saved to {output_file} (Using Streaming)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  To build index: python extract_logs.py --build <log_file>")
        print("  To extract logs: python extract_logs.py --extract <log_file> <YYYY-MM-DD>")
        sys.exit(1)

    command = sys.argv[1]
    log_file_path = sys.argv[2]

    if command == "--build":
        build_index(log_file_path)
    elif command == "--extract":
        if len(sys.argv) < 4:
            print("Error: Missing date argument")
            sys.exit(1)
        date = sys.argv[3]
        extract_logs(log_file_path, date)
    else:
        print("Invalid command. Use --build or --extract.")
