import datetime

# Path to your contributions file in the repo
file_path = "contributions.txt"

# Open the file and append the current date and time
with open(file_path, "a") as file:
    file.write(f"Contribution on: {datetime.datetime.now()}\n")
