from src.pipeline.preprocess import run_preprocessing


def run_pipeline(file: str):


    results = run_preprocessing(file)
    print(f"\n=== Pipeline Completed ===")

    return results
