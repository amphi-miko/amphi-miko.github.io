from pathlib import Path

counter_file = Path("number.txt")

value = int(counter_file.read_text().strip())
value += 1

counter_file.write_text(str(value) + "\n")

print(f"Counter updated to {value}")
