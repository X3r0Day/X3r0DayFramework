import os
import subprocess
import Framework_handler.fm_handler

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
    print("1 = Check for update\n")
    print("2 = Enter X3r0Day Framework\n")
    print("99 = Exit\n")
    
    opt = int(input("> "))
    
    if opt == 1:
        print("Checking for updates...")
        update_fm()

    elif opt == 2:
        print("Entering X3r0Day Framework")
        Framework_handler.fm_handler.main()


    elif opt == 99:
        exit()

    else:
        print("Error! Please try again!")