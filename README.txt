GPT-5.4
1. pip install openai

LLaMA
pip install llamafactory
    Setup bash:
    set API_PORT=8000
    set CUDA_VISIBLE_DEVICES=0
    llamafactory-cli api inference.yaml

    Setup windows:
    set API_PORT=8000
    set CUDA_VISIBLE_DEVICES=0
    llamafactory-cli api inference.yaml

Testbench in general
1. pip install -U transformers kernels torch
2. pip install python-dotenv

TCL Running
source /data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis_HLS/2024.1/settings64.sh
python testbench.py
vitis_hls -f run_hls.tcl ...