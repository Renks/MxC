# 🚀 Modal × ComfyUI

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Modal](https://img.shields.io/badge/modal-cloud-purple.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Run ComfyUI on the cloud for free with Modal's $30 monthly credits**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Volume Setup](#-volume-setup-guide) • [Download Models](#-downloading-models-manually) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

**Modal × ComfyUI** is a powerful solution that brings ComfyUI—a node-based UI for Stable Diffusion and other diffusion models—to the cloud, **completely free**. Leveraging [Modal.com](https://modal.com)'s generous $30 monthly credits, you can run advanced AI image generation workflows without managing expensive hardware or local GPU resources.

### Why Modal × ComfyUI?

- 🆓 **Free Cloud Computing**: Use Modal's $30 monthly credits (more than enough for most use cases)
- ⚡ **Serverless Infrastructure**: No setup, no maintenance, automatic scaling
- 🎨 **Full ComfyUI Support**: Access to all custom nodes, workflows, and models
- 💾 **Persistent Storage**: Keep your models and custom nodes across sessions
- 🔧 **Easy Configuration**: Simple INI-based config file for all settings
- 📦 **Auto-Setup**: Automated setup script handles dependencies and volume creation

---

## ✨ Features

- ✅ Cloud-based ComfyUI deployment on Modal.com
- ✅ Persistent volume storage for models and custom nodes
- ✅ Automatic dependency management for custom nodes
- ✅ GPU support (A10G, T4, P100, V100, A100)
- ✅ Web-based UI accessible from anywhere
- ✅ Configuration-driven setup (no hardcoding required)
- ✅ Interactive shell access for container debugging
- ✅ Support for Hugging Face and CivitAI model downloads

---

## 🚀 Quick Start

### Prerequisites

- Linux, macOS, or Windows (with WSL2)
- Python 3.11+
- uv ([link](https://docs.astral.sh/uv/getting-started/installation))
- Git
- Modal account ([sign up free](https://modal.com))

### ⚡ 30-Second Setup

```bash
# Clone the repository
git clone https://github.com/Renks/MxC.git
cd MxC

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install requirements
uv pip install -r requirements.txt

# Setup authentication (IMPORTANT!)
modal setup  # Follow browser authentication

# Configure your setup
python setup_modal.py

# Deploy and run
modal serve main.py
```

You will be given a public URL by the modal api, like so:

<div>
<sup>This output is for illustration purposes only.</sup>
<pre>
 ⋮
🔨 Created web endpoint for ComfyUIContainer.ui =>
    <span style="color: #ba6c66; padding:0.4rem; border: 2px solid red; font-weight: bold; cursor: pointer;">https://abc--appname-container-dev.modal.run</span>
 ⋮
</pre>
</div>

Open the endpoint in a web browser to use ComfyUI! 👏

While the following URL will be used for monitor your app:

<div>
<sup>This output is for illustration purposes only.</sup>
<pre>
 ⋮
✓ Initialized.
View run at <span style="color: #ba6c66; padding:0.4rem; border: 2px solid red; font-weight: bold; cursor: pointer;">https://modal.com/apps/your-modal-username/main/app-id</span>
✓ Created objects.
├── 🔨 Created mount /path/to/main.py
 ⋮
</pre>
</div>

---

## 📦 Installation

**Step 1: Clone the Repository**

```bash
git clone https://github.com/Renks/MxC.git
cd MxC
```

**Step 2: Create and Activate Virtual Environment**

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# On Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1

# On Windows (CMD)
# .venv\Scripts\activate.bat

```

**Step 3: Install Dependencies**

```bash
uv pip install -r requirements.txt
```

OR Manually (If you fancy yourself)

```bash
pip install modal==1.3.0.post1 pyyaml==6.0.3 python-dotenv==1.2.1 configparser==7.2.0
```

**Step 4: Authenticate with Modal**

**Linux and MacOS**

❗Please run this before you do anything else!

```bash
modal setup
```

This will open your browser to authenticate with Modal. Follow the prompts and return to the terminal.

**Windows (WSL2)**

🫷 For users running Windows Subsystem for Linux 2 (WSL2), the setup process requires an initial authentication step on the Windows host.

1. **Run Authentication on Windows:**

    Execute `modal setup` in your main Windows command prompt or PowerShell environment.

2. **Locate the Configuration File:**

    Successful authentication generates a `.modal.toml` file, typically saved in `%USERPROFILE%\.modal.toml`.

3. **Transfer to WSL2 Environment:**

    Copy this generated configuration file into your WSL2 home directory (~).

    **Example transfer command:**
    ```bash
    cp /mnt/c/Users/<your-windows-username>/.modal.toml ~/.modal.toml
    ```

**Step 5: Configure Your Project**

Edit [⚙️ config.ini](./config.ini) to customize your setup:

```ini
[RESOURCES]
gpu_type = t4              # Options: a10g, t4, p100, v100, a100
max_containers = 1
timeout = 3200

[FILESYSTEM]
volume_name = my-comfy-models
volume_mount_location = /root/per_comfy-storage
```

**Step 6: Run Setup Script**

```bash
python setup_modal.py
```

This script will:

✅ Create your persistent volume on Modal<br/>
❎ Download essential models from Hugging Face (Skipped - very slow) <br/>
✅ Set up the folder structure<br/>
✅ Install custom nodes and dependencies<br/>
✅ Generate extra_model_paths.yaml<br/>

**Step 7: Deploy and Run**

```bash
modal serve main.py
```

You'll see output like:

```bash
✓ Initialized. View run at https://modal.com/apps/<your-modal-username>/main/<app-id>
✓ Created objects.
├── 🔨 Created mount /path/to/main.py
├── 🔨 Created mount /path/to/extra_model_paths.yaml
├── 🔨 Created mount /path/to/config_comfyui.ini
├── 🔨 Created mount /path/to/comfy.settings.json
├── 🔨 Created mount /path/to/config.ini
├── 🔨 Created mount /path/to/.env
├── 🔨 Created mount PythonPackage:loaders
├── 🔨 Created mount /path/to/workflows
├── 🔨 Created function ComfyUIContainer.*.
└── 🔨 Created web endpoint for ComfyUIContainer.ui =>
    https://<your-modal-username>--comfyui-app-comfyuicontainer-ui-dev.modal.run
️️⚡️ Serving... hit Ctrl-C to stop!
├── Watching /path/to/workflows.
└── Watching /path/to/MxC.
--- Checking for custom node requirements ---
Installing requirements for: ComfyUI-GGUF
⋮
```

Open the endpoint in a web browser [https://your-modal-username--comfyui-app-comfyuicontainer-ui-dev.modal.run](https://your-modal-username--comfyui-app-comfyuicontainer-ui-dev.modal.run) to access ComfyUI!

---

## 📁 Volume Setup Guide

Default volume name is `my-comfy-models` but you can change it in [⚙️ config.ini](./config.ini) file

```ini
[FILESYSTEM]
; Name of the volume to be created for persistent storage. Diffusion models and custom nodes will be stored here
volume_name = my-fancy-volume-name-goes-here
```

Your Modal persistent volume should be organized like this:

```bash
📁 id-provided-by-modal-dot-com/    # this name will be different
├─ 📁 checkpoints/                  # manually download models here
│  ├─ 📄 model.safetensors
│  └─ 📄 flux-dev.safetensors
├─ 📁 custom_nodes/                 # add comfyui's custom_nodes here
│  ├─ 📁 ComfyUI-GGUF
│  ├─ 📁 rgthree-comfy
│  ├─ 📁 seedvr2_videoupscaler
│  └─ 📁 comfyui-controlnet-aux
├─ 📁 diffusion_models/             # manually download models here
│  ├─ 📄 z-image-turbo-Q8_0.gguf
│  ├─ 📄 qwen-image-edit-2511-Q4_1.gguf
│  ├─ 📄 seedvr2_ema_7b_fp16.safetensors
│  └─ 📄 seedvr2_ema_7b_sharp_fp16.safetensors
├─ 📁 loras/                        # manually download loras here
│  ├─ 📄 Qwen-Image-Edit-Lightning.safetensors
│  └─ 📄 flux-canny-controlnet-alpha.safetensors
├─ 📁 text_encoders/                # manually download clip models here
│  └─ 📄 qwen_2.5_vl_7b_fp8_scaled.safetensors
├─ 📁 unet/
│  └─ 📄 diffusion_pytorch_model.safetensors
└─ 📁 vae/                          # manually download vae(s) here
   ├─ 📄 ema_vae_fp16.safetensors
   └─ 📄 qwen_image_vae.safetensors
```

**Downloading Models**

~~The `setup_modal.py` script handles this automatically~~ (It was very slow and tedious). You can also manually add models:

Make sure you drop into your modal volume's shell first `modal shell --volume <your-volume-name>`
Once in, cd to volume using `cd /mnt/<your-volume-name>`

1. **From Hugging Face:**

    ```bash
    huggingface-cli download model-id --local-dir ./checkpoints
    ```

2. **From CivitAI:**

   - Download models via the web interface
   - Upload to your Modal volume using modal volume put

3. **Using Modal CLI:**

    ```bash
    modal volume put <your-volume-name> path/to/local/model/checkpoints/model.safetensors
    ```
4. **Using Wget CLI:**
    
    Instructions [here](#-downloading-models-manually).

---


## 🎁 Downloading Models (Manually)

The required directory structure is automatically generated upon the successful execution of `python setup_modal.py`. Make sure you ran `setup_modal.py` without any errors.

1. **Access the Volume Shell**

    Open an interactive shell session within your Modal volume:

    ```bash
    modal shell --volume <your-volume-name>
    ```
    _Note: Your volume will be mounted at `/mnt/<your-volume-name>`_.

2. **Navigate to the Target Directory**

    Change to the appropriate directory based on the model type:

    ```bash
    # For diffusion models:
    cd /mnt/<your-volume-name>/diffusion_models/

    # For checkpoints:
    cd /mnt/<your-volume-name>/checkpoints/
    ```

3. **Download Models via CLI**

    Identify your desired model on [Hugging Face](https://huggingface.co). We will use [unsloth/Z-Image-Turbo-GGUF](https://huggingface.co/unsloth/Z-Image-Turbo-GGUF/blob/main/z-image-turbo-Q8_0.gguf) as an example. Copy the direct download link for the file and use the `wget` utility to download it directly into the volume.

    **Example**
    ```bash
    wget https://huggingface.co/unsloth/Z-Image-Turbo-GGUF/resolve/main/z-image-turbo-Q8_0.gguf
    ```

    This command downloads `z-image-turbo-Q8_0.gguf` file directly into your _current working directory_ within the Modal volume.
    <br />
    Repeat for more models. You can also use `wget` utility to download `loras` and other files in their appropriate folders.

  
3. **Sync Changes (Important!)**

    Run `sync` command once you're done to save changes and then `exit`.

---

## 🎮 Usage

**Running ComfyUI**

```bash
# Start the Modal app
modal serve main.py

# Access the UI
# Open URL provided in console in your browser
```

**Interactive Shell Access (Debugging)**

To inspect the runtime environment or debug the filesystem, you can access the container using the following methods:

1. **Active Instance Attachment (Recommended)**
    
    While [⚡main.py](./main.py) is executing, run the following command in a separate terminal tab to attach an interactive shell to the running container:
    
    ```bash
    modal shell main.py     # in a new terminal tab ofcourse
    ```
    This allows you to manage the filesystem in real-time and install additional packages as needed within the active Modal volume.

2. **Legacy File Browsing (Deprecated)**

    Browse and debug the container filesystem:

    ```bash
    # Linux/macOS
    ./browsefs.sh

    # Windows (PowerShell)
    .\browsefs.ps1
    ```

**Managing Models and Custom Nodes**

```bash
# List files in your volume
modal volume ls <your-volume-name>

# Upload a model
modal volume put <your-volume-name> path/to/model.safetensors checkpoints/

# Download from volume
modal volume get <your-volume-name> checkpoints/model.safetensors ./local_path/
```

**Monitoring Your App**

```bash
# View logs
modal logs --app comfyui-app

# List running apps
modal app list
```

---

## ⚙️ Configuration

Edit [⚙️ config.ini](./config.ini) to customize your deployment:

```ini
[TOKENS]
HF_TOKEN = .env              # Store in .env file for security
CIVITAI_API_TOKEN = .env

[WEB]
port = 8000
host = 0.0.0.0

[FILESYSTEM]
volume_name = my-comfy-models
volume_mount_location = /root/per_comfy-storage
comfyui_dir = /root/comfy/ComfyUI

[RESOURCES]
gpu_type = a10g              # CPU if commented out
max_containers = 1
timeout = 3200
max_inputs = 10
cpu = 1
memory = 16384

[MODEL_PATHS]
checkpoints =
    models/checkpoints/
    /root/per_comfy-storage/checkpoints/
loras =
    models/loras/
    /root/per_comfy-storage/loras
```
**🚧 Documentation in Progress**<br />
More instructions will be added later. Please refer to the inline comments within [⚙️ config.ini](./config.ini) for detailed parameter descriptions and setup instructions.

---

## 🔐 Security

- **API Keys**: Store tokens in a .env file (never commit to git)
- **Volume Access**: Only accessible within Modal containers
- **Authentication**: Modal handles all infrastructure security
- **Data Privacy**: Models stay in your isolated container

Create a `.env` file:

Token values are optional but make sure keys exist. You can rename `.env.BAK` to `.env` for ease.

```ini
HF_TOKEN=your_huggingface_token
CIVITAI_API_TOKEN=your_civitai_token
```

---

## 📊 Cost Breakdown

| Resource          |  Cost  | Modal Credits |
| ----------------- | :----: | :-----------: |
| A10G GPU (1 hour) | ~$1.50 | 0.05 credits  |
| T4 GPU (1 hour)   | ~$0.35 | 0.01 credits  |
| Storage           |  Free  |     Free      |
| Monthly Budget    |  ~$45  |      $30      |

**You get $30 credits per month** = **free unlimited usage!**

---

## 🛠️ Troubleshooting

**Virtual Environment Not Activating**

```bash
# Recreate the venv
rm -rf .venv
uv venv    # OR 'python3.11 -m venv .venv'
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Modal Authentication Failed**

```bash
rm ~/.modal.toml    # Windows (CMD): del "%USERPROFILE%\.modal.toml"
modal setup         # Re-authenticate
```

**Volume Not Found**

```bash
# List all volumes
modal volume list

# Create volume if missing
modal volume create my-comfy-models
```

**Check the running container(s)**

```bash
# List all running containers with their ID
modal container list

# Attach shell to a specific container 
modal shell <Container ID>

```

**Models Not Loading**

Check the volume structure:

```bash
modal volume ls my-comfy-models diffusion_models/
#   OR
modal volume ls my-comfy-models checkpoints/
```

---

## 📚 Project Structure

```bash
📁 MxC/
├─📁 workflows/                 # ComfyUI workflow templates (will be uploaded)
│ └─📄 README.md                # README for workflows (auto-generated)
│ └─📄 example_workflow.json    # Dummy workflow (doesn't exist)
├─📄 README.md                  # This file
├─📄 setup_modal.py             # Setup and initialization script
├─📄 main.py                    # Main Modal app
├─📄 loaders.py                 # Python library to load and parse config.ini file
├─📄 generate_model_paths.py    # YAML config generator
├─📄 config.ini                 # Configuration file for the project (Important)
├─📄 requirements.txt           # Python dependencies
├─📄 extra_model_paths.yaml     # ComfyUI's extra paths (will be uploaded to container)
├─📄 comfy.settings.json        # Settings for ComfyUI (will be uploaded to container)
├─📄 config_comfyui.ini         # Settings for ComfyUI's Manager (will also be uploaded)
├─📄 .env.BAK                   # Environment variables template
├─📄 .env                       # Environment variables (Store your tokens here)
├─📄 .emptyfile                 # Used for creating directories inside Modal volume
├─📄 pyproject.toml             # Project file (ignore)
└─📄 uv.lock                    # Project file (ignore)
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [Modal.com](https://modal.com) - For incredible free cloud compute credits
- [ComfyUI](https://www.comfy.org) - For the amazing node-based UI
- [Hugging Face](https://huggingface.co) - For model hosting and APIs

---

## 📞 Support

- 📖 [Modal Documentation](https://modal.com/docs/guide)
- 🐛 [ComfyUI Issues](https://github.com/Comfy-Org/ComfyUI)
- 💬 [Modal Community](modal.com/slack)

---

<div align="center">

[⬆ back to top](#-modal--comfyui)

Made with ❤️ for the AI community

</div>
