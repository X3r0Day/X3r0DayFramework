import os
import subprocess

def update_fm():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)

    print("Fetching updates from GitHub...")
    fetch_process = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True)

    status_process = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True)
    
    if "Your branch is up to date" in status_process.stdout:
        print("No updates available.")
    else:

        print("Updates found, pulling the latest changes...")
        pull_process = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)
        
        if pull_process.returncode == 0:
            print("Repository updated successfully!")
        else:
            print("Failed to update the repository.")
            print(pull_process.stderr)

while True:
    print("X3r0Day Toolkit\n")
    print("1 = Check for update")
    print("2 = Enter The Framework")
    print("99 = Exit")
    
    opt = int(input("> "))
    
    if opt == 1:
        print("Checking for updates...")
        update_fm()

    elif opt == 2:
        print("Enter X3r0Day Framework")
    elif opt == 99:
        break
