import pandas as pd
import subprocess
n= [8,3,7,4]
l = [2,6,5]
df = pd.read_csv("JobsData.csv")
num_job = 7-2 # len(df)

for i in range(1):
    print(f"Running job {i}...")
    subprocess.run(["python", "1Score.py", str(num_job)])
    subprocess.run(["python", "2CL.py", str(num_job)])
    subprocess.run(["python", "3Bro5.py", str(num_job)])
    subprocess.run(["python", "4Mail.py", str(num_job)])