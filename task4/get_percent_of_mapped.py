import subprocess
import sys
from pathlib import Path
import re

def main():
    reference_path = Path(sys.argv[1])
    reads_path = Path(sys.argv[2])

    subprocess.run(['fastqc', reads_path])

    subprocess.run(['bwa', 'index', reference_path])

    subprocess.run(f'bwa mem {reference_path} {reads_path} > aligned.sam', shell=True)

    analysis = subprocess.run(['samtools', 'flagstat', 'aligned.sam'], capture_output = True, text=True)
    
    pattern = r"mapped \((\d+\.\d+)%"
    matching = re.search(pattern, analysis.stdout)
    if matching:
        percentage = matching.group(1)
        if float(percentage) > 0.9:
            print(f'OK: mapped {percentage}%')
            return
        print(f'not OK: mapped {percentage}%')
    else:
        print('No mapped percentage found')

if __name__ == '__main__':
    main()
