import os

def get_model_str(model_name: str) -> str:
    if not os.path.splitext(model_name)[1]:
        model_name += ".txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, model_name)

    try:
        with open(file_path, "r") as file:
            model_str = file.read()
        return model_str
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None
