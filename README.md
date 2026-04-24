Steps to launch vitis python script:
1. source /data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1/settings64.sh
2. export AIE_PLATFORM=/data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1/base_platforms/xilinx_vek280_base_202410_1/xilinx_vek280_base_202410_1.xpfm
3. command: vitis -i
4. Once in vitis interactive shell: run <python script>.py

Testbench in general
1. pip install -U transformers kernels torch

Vitis_Helper
1. pip install "protobuf==3.20*"

How to install trained models to run testbench on
Since the models are too large for Github, they are stored on HuggingFace. We will install the models on our machine locally, and call them in our code.
1. Activate your python environment:
    module load mamba/latest
    eval "$(mamba shell hook --shell bash)"
    mamba activate llm_debug
2. Install required Python packages
    pip install --upgrade pip
    pip install torch transformers huggingface_hub accelerate
    pip install bitsandbytes
3. The model will be stored in ../Collab_Models
    run download_codestral.py located in the ../Collab_Models folder to install the model
    You should see a folder created in ../Collab_Models containing the the downloaded model