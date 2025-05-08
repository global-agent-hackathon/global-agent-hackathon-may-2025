from pathlib import Path

# Get the directory where the current script is located
script_dir = Path(__file__).parent.resolve()

# Construct the path to CV.pdf relative to the script location
resume_path = (script_dir / 'CV.pdf').resolve()
print(resume_path)