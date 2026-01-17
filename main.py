import subprocess
from pathlib import Path
import modal
from loaders import ConfigLoader

# ===========================
# Global Configuration
# ===========================

# Modal app name
APP_NAME = "comfyui-app"

# Absolute path of current working directory
CURRENT_DIR = Path(__file__).parent.resolve()

# Load configurations from config.ini
cfg = ConfigLoader(config_path="config.ini", env_path=".env").load_configs()
HF_TOKEN = str(cfg["tokens"]["hf_token"])
CIVITAI_API_TOKEN = str(cfg["tokens"]["civitai_api_token"])
WEB_SERVER_HOST = str(cfg["web"]["host"])
WEB_SERVER_PORT = cfg["web"]["port"]
VOLUME_NAME = str(cfg["filesystem"]["volume_name"])
VOLUME_MOUNT_LOCATION = str(cfg["filesystem"]["volume_mount_location"])
COMFYUI_DIR = str(cfg["filesystem"]["comfyui_dir"])
CUSTOM_NODES_DIR = str(cfg["filesystem"]["custom_nodes_dir"])
CUSTOM_OUTPUT_DIR = str(cfg["filesystem"]["custom_output_dir"]) # "/root/per_comfy-storage/output"
GPU_TYPE = str(cfg["resources"]["gpu_type"]) or None
CPU = cfg["resources"]["cpu"]
MEMORY = cfg["resources"]["memory"]
MAX_CONTAINERS = cfg["resources"]["max_containers"]
SCALEDOWN_WINDOW = cfg["resources"]["scaledown_window"]
TIMEOUT = cfg["resources"]["timeout"]
MAX_INPUTS = cfg["resources"]["max_inputs"]

def debug_print_config_and_exit():
    """Utility function to print configuration and exit."""
    # Debug prints
    # Print all of the above variables and exit
    print("Configuration Loaded:")
    print(f"APP_NAME: {APP_NAME}")
    print(f"CURRENT_DIR: {CURRENT_DIR}")
    print(f"HF_TOKEN: {HF_TOKEN}")
    print(f"CIVITAI_API_TOKEN: {CIVITAI_API_TOKEN}")
    print(f"WEB_SERVER_HOST: {WEB_SERVER_HOST}")
    print(f"WEB_SERVER_PORT: {WEB_SERVER_PORT}")
    print(f"VOLUME_NAME: {VOLUME_NAME}")
    print(f"VOLUME_MOUNT_LOCATION: {VOLUME_MOUNT_LOCATION}")
    print(f"COMFYUI_DIR: {COMFYUI_DIR}")
    print(f"CUSTOM_NODES_DIR: {CUSTOM_NODES_DIR}")
    print(f"GPU_TYPE: {GPU_TYPE}")
    print(f"CPU: {CPU}")
    print(f"MEMORY: {MEMORY}")
    print(f"MAX_CONTAINERS: {MAX_CONTAINERS}")
    print(f"SCALEDOWN_WINDOW: {SCALEDOWN_WINDOW}")
    print(f"TIMEOUT: {TIMEOUT}")
    print(f"MAX_INPUTS: {MAX_INPUTS}")
    exit(1)

# debug_print_config_and_exit()

# ===========================
# Modal Image Configuration
# ===========================

# Define the Modal image
comfy_image = (
    modal.Image.debian_slim(python_version="3.11")
    .env({"HF_TOKEN": HF_TOKEN, "CIVITAI_API_TOKEN": CIVITAI_API_TOKEN})
    .apt_install(
        "git", "nano",
        "libgl1", "libglib2.0-0", "libsm6", "libxext6", "libxrender1"  # OpenCV dependencies
    )
    .pip_install("comfy-cli", "gguf", "sentencepiece", "opencv-python-headless")
    .run_commands("comfy --skip-prompt install --nvidia")
    .run_commands(
        # Some Useful Custom Nodes (Optional)
        "comfy node install ComfyUI-Crystools",  # For Resource monitor
        "comfy node install comfyui-easy-use",
        "comfy node install comfyui-kjnodes",
        "comfy node install comfyui_ultimatesdupscale",
        "comfy node install comfyui_essentials",
        "comfy node install comfyui-detail-daemon",
        "comfy node install seedvarianceenhancer",
        "comfy node install comfyui_controlnet_aux",
    )
    # Add loaders.py file for configuration loading inside the container
    .add_local_python_source("loaders", copy=False)
    .add_local_file(str(CURRENT_DIR / "config.ini"), remote_path="/root/config.ini")
    .add_local_file(str(CURRENT_DIR / ".env"), remote_path="/root/.env")
    # Persistent comfyui settings and workflows
    # v0.3.76+ (with System User API) # https://github.com/Comfy-Org/ComfyUI-Manager#paths
    .add_local_file(str(CURRENT_DIR / "extra_model_paths.yaml"), remote_path=str(COMFYUI_DIR + "/extra_model_paths.yaml"))
    .add_local_file(str(CURRENT_DIR / "config_comfyui.ini"), remote_path=str(COMFYUI_DIR + "/user/__manager/config.ini"))
    .add_local_file(str(CURRENT_DIR / "comfy.settings.json"), remote_path=str(COMFYUI_DIR + "/user/default/comfy.settings.json"))
    .add_local_dir(str(CURRENT_DIR / "workflows/"), remote_path=str(COMFYUI_DIR + "/user/default/workflows/"))
)

# ===========================
# Modal App Configuration
# ===========================

app = modal.App(name=APP_NAME, image=comfy_image)

# Create a persistent volume
model_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# Prepare the container arguments dynamically
container_kwargs = {
    "max_containers": MAX_CONTAINERS,
    "scaledown_window": SCALEDOWN_WINDOW,
    "timeout": TIMEOUT,
    "gpu": GPU_TYPE,
    "volumes": {VOLUME_MOUNT_LOCATION: model_volume},
}

# Only add CPU and Memory if they actually have values
if CPU is not None:
    container_kwargs["cpu"] = CPU

if MEMORY is not None:
    container_kwargs["memory"] = MEMORY

# Use dictionary unpacking (**) to pass the arguments
@app.cls(**container_kwargs)
@modal.concurrent(max_inputs=MAX_INPUTS)

class ComfyUIContainer:
    @modal.enter()
    def setup_dependencies(self):
        """
        Scans the persistent custom_nodes directory for requirements.txt files
        and installs the dependencies.
        """
        nodes_path = Path(CUSTOM_NODES_DIR)

        if not nodes_path.exists():
            print("No custom_nodes directory found; skipping dependency check.")
            return

        print("--- Checking for custom node requirements ---")
        for node_dir in nodes_path.iterdir():
            if node_dir.is_dir():
                req_file = node_dir / "requirements.txt"
                if req_file.exists():
                    print(f"Installing requirements for: {node_dir.name}")
                    # Install dependencies for each node
                    subprocess.run(
                        ["pip", "install", "-r", str(req_file)], check=False)
        print("--- Dependency check complete ---")

    @modal.web_server(WEB_SERVER_PORT, startup_timeout=60)
    def ui(self):
        """
        Launches the ComfyUI web server.
        """
        print(f"Starting ComfyUI on  {WEB_SERVER_HOST}:{WEB_SERVER_PORT}...")
        subprocess.Popen(
            f"comfy launch -- --output-directory {CUSTOM_OUTPUT_DIR} --listen {WEB_SERVER_HOST} --port {WEB_SERVER_PORT}",
            shell=True
        )
