Steps to launch vitis python script:
1. module load mamba
2. source activate <environment name>
3. ./run_vitis.sh testbench

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