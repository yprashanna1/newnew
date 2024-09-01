import subprocess

def install_spacy_model():
    try:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
        print("Successfully installed en_core_web_sm")
    except subprocess.CalledProcessError as e:
        print(f"Error installing en_core_web_sm: {e}")

if __name__ == "__main__":
    install_spacy_model()
