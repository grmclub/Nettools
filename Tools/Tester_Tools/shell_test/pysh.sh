import os
import subprocess

def run_custom_shell():
    while True:
        try:
            # Replicate a standard bash prompt layout
            cwd = os.getcwd()
            user_input = input(f"py-shell:{cwd}$ ").strip()
            
            if not user_input:
                continue
                
            # Handle the 'exit' command natively
            if user_input == "exit":
                break
                
            # Handle directory changes ('cd') inside the Python process context
            if user_input.startswith("cd "):
                path = user_input[3:].strip()
                try:
                    os.chdir(path)
                except FileNotFoundError:
                    print(f"cd: no such file or directory: {path}")
                continue
            
            # Execute all other standard commands via bash execution
            subprocess.run(user_input, shell=True, executable="/bin/bash")
            
        except (KeyboardInterrupt, EOFError):
            print("\nUse 'exit' to leave the shell.")

if __name__ == "__main__":
    run_custom_shell()
