import requests
import concurrent.futures
from urllib.parse import urlparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from colorama import Style, Fore
from time import sleep
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# That one intro
intro=f"""{Style.BRIGHT}{Fore.LIGHTGREEN_EX}

▒██   ██▒  ██████   ██████      ██████  ▄████▄   ▄▄▄       ███▄    █  ███▄    █ ▓█████  ██▀███  
▒▒ █ █ ▒░▒██    ▒ ▒██    ▒    ▒██    ▒ ▒██▀ ▀█  ▒████▄     ██ ▀█   █  ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒
░░  █   ░░ ▓██▄   ░ ▓██▄      ░ ▓██▄   ▒▓█    ▄ ▒██  ▀█▄  ▓██  ▀█ ██▒▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒
 ░ █ █ ▒   ▒   ██▒  ▒   ██▒     ▒   ██▒▒▓▓▄ ▄██▒░██▄▄▄▄██ ▓██▒  ▐▌██▒▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄  
▒██▒ ▒██▒▒██████▒▒▒██████▒▒   ▒██████▒▒▒ ▓███▀ ░ ▓█   ▓██▒▒██░   ▓██░▒██░   ▓██░░▒████▒░██▓ ▒██▒
▒▒ ░ ░▓ ░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░   ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
░░   ░▒ ░░ ░▒  ░ ░░ ░▒  ░ ░   ░ ░▒  ░ ░  ░  ▒     ▒   ▒▒ ░░ ░░   ░ ▒░░ ░░   ░ ▒░ ░ ░  ░  ░▒ ░ ▒░
 ░    ░  ░  ░  ░  ░  ░  ░     ░  ░  ░  ░          ░   ▒      ░   ░ ░    ░   ░ ░    ░     ░░   ░ 
 ░    ░        ░        ░           ░  ░ ░            ░  ░         ░          ░    ░  ░   ░     
                                       ░                                                        

{Style.RESET_ALL}{Fore.YELLOW}
Welcome to X3r0Day Framework's XSS Scanner!                                       
{Style.RESET_ALL}"""

print(intro)
sleep(2)

def normalize_url(url):
    parsed_url = urlparse(url)
    return "http://" + url if not parsed_url.scheme else url


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def parse_request_file(request_file):
    with open(request_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    method = lines[0].split(" ")[0]
    url = lines[0].split(" ")[1]
    headers = {}
    body = None

    for line in lines[1:]:
        if line == "\n":
            body = "".join(lines[lines.index(line) + 1:]).strip()
            break
        header_parts = line.split(": ", 1)
        if len(header_parts) == 2:
            headers[header_parts[0]] = header_parts[1].strip()

    return method, normalize_url(url), headers, body


def test_xss_payload(session, method, url, headers, body, payload, timeout):
    try:
        modified_body = body.replace("XERODAY", payload) if body else None
        modified_url = url.replace("XERODAY", payload)

        response = (
            session.get(modified_url, headers=headers, timeout=timeout)
            if method == "GET"
            else session.post(modified_url, headers=headers, data=modified_body, timeout=timeout)
        )

        if payload in response.text:
            logging.info(f"{Fore.GREEN}[!] XSS Found with payload: {payload}{Style.RESET_ALL}")
            return payload
        else:
            logging.debug(f"{Fore.RED}[-] Payload not reflected: {payload}{Style.RESET_ALL}")
    except requests.RequestException as e:
        logging.error(f"[Error] Could not test payload '{payload}': {e}")
    return None


def xss_fm(method, url, headers, body, payloads, timeout=10, max_threads=10):
    logging.info(f"Testing URL: {url}")
    vulnerabilities = []

    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        with requests_retry_session() as session:
            futures = {
                executor.submit(test_xss_payload, session, method, url, headers, body, payload.strip(), timeout): payload
                for payload in payloads
            }

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    vulnerabilities.append(result)

    logging.info(f"[+] Total Vulnerabilities Found: {len(vulnerabilities)}")
    return vulnerabilities


def get_payloads(payload_file):
    try:
        with open(payload_file, "r", encoding="utf-8") as f:
            payloads = f.readlines()
            if not payloads:
                raise ValueError("Payload file is empty.")
        return payloads
    except Exception as e:
        logging.error(f"[Error] {e}")
        return []


def handle_user_choice(choice, payloads):
    try:
        if choice == "1":
            # Test with Burp Suite request file
            request_file = input("\nEnter the path to the Burp Suite request file: ").strip()
            method, url, headers, body = parse_request_file(request_file)
            timeout = int(input("Enter request timeout (default 10): ").strip() or 10)
            logging.info("\n[+] Testing Burp Suite request file...")
            xss_fm(method, normalize_url(url), headers, body, payloads, timeout)

        if choice == "2":
            # Test with Direct URL
            url = input("\nEnter the URL to test (use 'XERODAY' as placeholder): ").strip()
            method = input("Enter HTTP method (GET/POST): ").strip().upper()
            body = None
            if method == "POST":
                body = input("Enter request body (use 'XERODAY' as placeholder): ").strip()
            headers = {}
            timeout = int(input("Enter request timeout (default 10): ").strip() or 10)
            logging.info("\n[+] Testing Direct URL...")
            xss_fm(method, normalize_url(url), headers, body, payloads, timeout)

        if choice == "3":
            # Test both
            # Burp Suite request file
            request_file = input("\nEnter the path to the Burp Suite request file: ").strip()
            method, url, headers, body = parse_request_file(request_file)
            timeout = int(input("Enter request timeout (default 10): ").strip() or 10)
            logging.info("\n[+] Testing Burp Suite request file...")
            xss_fm(method, normalize_url(url), headers, body, payloads, timeout)

            # Direct URL
            url = input("\nEnter the URL to test (use 'XERODAY' as placeholder): ").strip()
            method = input("Enter HTTP method (GET/POST): ").strip().upper()
            body = None
            if method == "POST":
                body = input("Enter request body (use 'XERODAY' as placeholder): ").strip()
            headers = {}
            timeout = int(input("Enter request timeout (default 10): ").strip() or 10)
            logging.info("\n[+] Testing Direct URL...")
            xss_fm(method, normalize_url(url), headers, body, payloads, timeout)

    except Exception as e:
        logging.error(f"[Error] {e}")


# Main Function
def main():
    payload_file = input("Enter the path of the XSS payload file: ").strip()
    payloads = get_payloads(payload_file)
    if not payloads:
        return

    print("\nDo you want to test using:")
    print("1. Burp Suite request file")
    print("2. Direct URL")
    print("3. Test both (Request and Direct URL)")
    choice = input("> ").strip()

    handle_user_choice(choice, payloads)


if __name__ == "__main__":
    main()
