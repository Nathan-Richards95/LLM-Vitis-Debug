from huggingface_hub import snapshot_download
from pathlib import Path
import os
import constants

def main():
    constants.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print("Available models:")
    for key, info in constants.AVAILABLE_MODELS.items():
        print(f"{key}. {info['name']} ({info['repo_id']})")

    print("\nEnter the numbers of the models you want to download.")
    print("Example: 1,2 or 3")
    choice = input("Selection: ").strip()

    selected_keys = [x.strip() for x in choice.split(",") if x.strip()]

    for key in selected_keys:
        if key not in AVAILABLE_MODELS:
            print(f"Skipping invalid selection: {key}")
            continue

        info = constants.AVAILABLE_MODELS[key]
        local_dir = constants.MODEL_DIR / info["name"]

        print(f"\nDownloading {info['name']}...")
        print(f"Repo: {info['repo_id']}")
        print(f"Local dir: {local_dir}")

        snapshot_download(
            repo_id=info["repo_id"],
            local_dir=str(local_dir),
            local_dir_use_symlinks=False
        )

        print(f"Finished downloading {info['name']}")

    print("\nDone.")


if __name__ == "__main__":
    main()