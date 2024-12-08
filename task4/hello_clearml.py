from clearml import PipelineController, Logger

def log_hello(reads_path: str):
    Logger.current_logger().report_text("HELLO CLEARML")


if __name__ == "__main__":

    pipe = PipelineController(name="Hello ClearML", project="Bioinformatics")
    pipe.set_default_execution_queue("default")


    pipe.add_function_step(
        name="log_hello",
        function=log_hello,
    )

    pipe.start_locally(run_pipeline_steps_locally = True)
