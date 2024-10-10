import subprocess
import concurrent.futures
import sys

# Function to perform the dig axfr command
def perform_axfr(subdomain, domain, ip):
    # Replace FUZZ with the subdomain from the wordlist
    full_domain = f"{subdomain}.{domain}"
    
    # Perform the dig axfr command
    command = ["dig", "axfr", full_domain, f"@{ip}"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        # Check if the output contains successful zone transfer
        if "Transfer failed." not in result.stdout and "connection timed out" not in result.stdout:
            return full_domain, result.stdout.strip()
    except subprocess.TimeoutExpired:
        pass
    return None, None

# Main function to read the wordlist and perform the AXFR check concurrently
def main(domain, ip, wordlist_file):
    with open(wordlist_file, 'r') as file:
        wordlist = file.read().splitlines()
    
    # Using ThreadPoolExecutor to execute requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(perform_axfr, word, domain, ip): word for word in wordlist}
        
        found_any = False
        for future in concurrent.futures.as_completed(futures):
            full_domain, result = future.result()
            if result:
                found_any = True
                print(f"[SUCCESS] Zone transfer for {full_domain}:\n{result}\n{'-'*60}")
        
        if not found_any:
            print("No successful zone transfers found.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 axfr_fuzz.py <domain> <ip> <wordlist>")
        sys.exit(1)
    
    domain = sys.argv[1]
    ip = sys.argv[2]
    wordlist_file = sys.argv[3]
    
    main(domain, ip, wordlist_file)
