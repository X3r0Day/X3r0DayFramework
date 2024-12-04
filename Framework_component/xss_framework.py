import requests
import threading
from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import concurrent.futures

def normalize_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return "http://" + url
    return url

def requests_retry_session(
    retries=3, 
    backoff_factor=0.3, 
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Parse Burp Suite Request
def parse_request_file(request_file):
    with open(request_file, 'r') as f:
        lines = f.readlines()

    method = lines[0].split(' ')[0]
    url = lines[0].split(' ')[1]
    headers = {}
    body = None

    for line in lines[1:]:
        if line == '\n':
            body = ''.join(lines[lines.index(line) + 1:]).strip()
            break
        header_parts = line.split(': ', 1)
        if len(header_parts) == 2:
            headers[header_parts[0]] = header_parts[1].strip()

    return method, normalize_url(url), headers, body

def test_xss_payload(session, method, url, headers, body, payload, proxies, timeout):
    try:
        modified_body = body.replace("XERODAY", payload) if body else None
        modified_url = url.replace("XERODAY", payload)

        if method == 'GET':
            response = session.get(modified_url, headers=headers, proxies=proxies, timeout=timeout)
        elif method == 'POST':
            response = session.post(modified_url, headers=headers, data=modified_body, proxies=proxies, timeout=timeout)
        else:
            print(f"[Error] Unsupported HTTP method: {method}")
            return None

        if payload in response.text:
            print(f"[!] XSS Found with payload: {payload}")
            return payload
        else:
            print(f"[-] Payload not reflected: {payload}")
    except requests.exceptions.RequestException as e:
        print(f"[Error] Could not test payload '{payload}': {e}")
    return None

def xss_fm(method, url, headers, body, payloads, proxies=None, timeout=10, max_threads=50):
    print(f"\nTesting URL: {url}")
    vulnerabilities = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        with requests_retry_session() as session:
            futures = []
            for payload in payloads:
                payload = payload.strip()
                futures.append(executor.submit(test_xss_payload, session, method, url, headers, body, payload, proxies, timeout))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    vulnerabilities.append(result)

    print(f"\n[*] Testing completed for this request.")
    print(f"[+] Total Vulnerabilities Found: {len(vulnerabilities)}")
    return vulnerabilities

def main():
    print("Welcome to X3r0Day's Improved XSS Framework!")

    payload_file = input("Enter the path of the XSS payload file: ").strip()
    try:
        with open(payload_file, 'r') as f:
            payloads = f.readlines()
            if not payloads:
                print("[Error] Payload file is empty. Please provide valid payloads.")
                return
    except FileNotFoundError:
        print(f"[Error] File not found: {payload_file}")
        return

    print("\nDo you want to test using:")
    print("1. Burp Suite request file")
    print("2. Direct URL")
    choice = input("> ").strip()

    headers = {}
    body = None
    proxies = {}
    timeout = 10

    if choice == '1':
        request_file = input("Enter the path to the Burp Suite request file: ").strip()
        try:
            method, url, headers, body = parse_request_file(request_file)
        except FileNotFoundError:
            print(f"[Error] File not found: {request_file}")
            return
        except Exception as e:
            print(f"[Error] Failed to parse Burp Suite request file: {e}")
            return
    elif choice == '2':
        url = input("Enter the URL you want to test for XSS vulnerability (use 'XERODAY' as placeholder): ").strip()
        method = input("Enter the HTTP method (GET or POST): ").strip().upper()
        if method not in ['GET', 'POST']:
            print("[Error] Invalid HTTP method. Please choose GET or POST.")
            return

        if method == 'POST':
            body = input("Enter the request body (use 'XERODAY' as placeholder): ").strip()

    else:
        print("[Error] Invalid choice.")
        return

    use_proxy = input("\nDo you want to use a proxy? (y/n): ").strip().lower()
    if use_proxy == 'y':
        proxy_url = input("Enter proxy URL (e.g., http://127.0.0.1:8080): ").strip()
        proxies = {"http": proxy_url, "https": proxy_url}

    timeout_input = input("Enter request timeout in seconds (default 10): ").strip()
    if timeout_input.isdigit():
        timeout = int(timeout_input)

    xss_fm(method, normalize_url(url), headers, body, payloads, proxies, timeout)

if __name__ == "__main__":
    main()
