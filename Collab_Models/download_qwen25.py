from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="SiddharthaChekuri/qwen2.5-32b-aie-merged",
    local_dir="Collab_Models/qwen2.5-32b-aie-merged",
    local_dir_use_symlinks=False
)