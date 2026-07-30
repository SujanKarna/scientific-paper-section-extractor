from src.pipeline.file_loader import save_uploaded_file
from src.pipeline.preprocess import run_preprocessing


def run_pipeline(file: str):

    print("\n=== Step 1: Saving File ===")
    saved_file_path = save_uploaded_file(file)
    print(f"File saved to: {saved_file_path}")


    results = run_preprocessing(saved_file_path)
    print(f"\n=== Pipeline Completed ===")



if __name__ == "__main__":
    run_pipeline("C:\\Users\\karna\\Downloads\\sample.pdf") # Provide the dir to your file in your device