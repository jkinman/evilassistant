from .assistant import run_assistant

def main():
    try:
        run_assistant()
    except KeyboardInterrupt:
        print("Stopped")

if __name__ == "__main__":
    main()
