from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="SiddharthaChekuri/codestral-22b-aie-merged",
    local_dir="Collab_Models/codestral-22b-aie-merged",
    local_dir_use_symlinks=False
)