from clearml import PipelineController, Logger
import subprocess
import re
import sys



def fastqc_step(reads_path: str):
    Logger.current_logger().report_text("fastqc_step")
    subprocess.run(['fastqc', reads_path])

def bwa_index_step(reference_path: str):
    Logger.current_logger().report_text("bwa_index_step")
    subprocess.run(['bwa', 'index', reference_path])

def bwa_alignment_step(reference_path: str, reads_path: str):
    Logger.current_logger().report_text("bwa_alignment_step")
    subprocess.run(f'bwa mem {reference_path} {reads_path} > aligned.sam', shell=True)

def samtools_flagstat_step():
    Logger.current_logger().report_text("samtools_flagstat_step")
    analysis = subprocess.run(['samtools', 'flagstat', 'aligned.sam'], capture_output = True, text=True)
    pattern = r"mapped \((\d+\.\d+)%"
    matching = re.search(pattern, analysis.stdout)
    if matching:
        percentage = matching.group(1)
        if float(percentage) > 0.9:
            Logger.current_logger().report_text(f'OK: mapped {percentage}%')
            return
        Logger.current_logger().report_text(f'not OK: mapped {percentage}%')
    else:
        Logger.current_logger().report_text("'No mapped percentage found'")


if __name__ == "__main__":

    reference_path = sys.argv[1]
    reads_path = sys.argv[2]
    pipe = PipelineController(name="Mapping Quality Pipeline", project="Bioinformatics")
    pipe.set_default_execution_queue("default")


    pipe.add_function_step(
        name="FastQC Analysis",
        function=fastqc_step,
        function_kwargs={'reads_path': reads_path} 
    )

    pipe.add_function_step( 
        name="BWA Indexing",
        function=bwa_index_step,
        parents = ['FastQC Analysis'],
        function_kwargs={'reference_path': reference_path} 
    )

    pipe.add_function_step(
        name="BWA Alignment",
        function=bwa_alignment_step,
        parents = ['BWA Indexing'],
        function_kwargs={
            'reference_path': reference_path, 
            'reads_path': reads_path,  
        }
    )

    pipe.add_function_step(
        name="Samtools Flagstat",
        parents = ['BWA Alignment'],
        function=samtools_flagstat_step,
    )
    

    pipe.start_locally(run_pipeline_steps_locally = True)
