#!/usr/bin/env python3
import requests
import argparse
from colorama import Fore, Style, init

# colorama to auto-reset after each print statement
init(autoreset=True)

# get the latest version of a package from PyPI
def get_latest_version(package_name: str) -> str:
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['info']['version']
    except requests.RequestException as e:
        print(f"{Fore.YELLOW}Error fetching data for {package_name}: {e}")
        return None

# process the requirements.txt file and optionally update it
def check_and_update_versions(file_path: str, update: bool = False):
    updated_lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if '==' in line or '>=' in line:
            operator = '==' if '==' in line else '>='
            package_name, current_version = line.split(operator)
            package_name = package_name.strip()
            current_version = current_version.strip()
            latest_version = get_latest_version(package_name)
            
            if latest_version:
                if current_version != latest_version:
                    print(f"{Fore.RED}{package_name}: Current version - {current_version}, Latest version - {latest_version}")
                    if update:
                        line = f"{package_name}{operator}{latest_version}\n"
                else:
                    print(f"{Fore.GREEN}{package_name}: Current version - {current_version} is up to date.")
            else:
                print(f"{Fore.YELLOW}{package_name}: Could not fetch latest version")
        updated_lines.append(line)
    
    if update:
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)
        print(f"{Fore.GREEN}requirements.txt has been updated with the latest versions.")

# Adding argument parsing to accept an "update" flag
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check and optionally update package versions in requirements.txt.")
    parser.add_argument("-u", "--update", action="store_true", help="Update the requirements.txt file with the latest versions of the packages.")
    parser.add_argument("-f", "--file", type=str, help="Path to the requirements.txt file.", default="requirements.txt")
    args = parser.parse_args()
    
    check_and_update_versions(args.file, args.update)
