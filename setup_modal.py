#!/usr/bin/env python3
"""
Setup script for Modal × ComfyUI
Automates volume creation, model downloading, folder structure setup, and configuration generation.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import shutil

try:
    from loaders import ConfigLoader
    from generate_model_paths import generate_extra_model_paths
except ImportError:
    print("Error: Required modules not found. Make sure you're in the project root directory.")
    sys.exit(1)

class ModalSetup:
    """Handles the complete setup process for Modal × ComfyUI."""

    def __init__(self):
        self.project_dir = Path(__file__).parent.resolve()
        self.config = None
        self.load_config()

    def load_config(self):
        """Load configuration from config.ini"""
        # Check if .env exists and create if not
        env_file = self.project_dir / ".env"
        if not env_file.exists():
            print("⚠️ .env file not found. Creating from template...")
            self.setup_env_file()
        
        try:
            loader = ConfigLoader(
                config_path=str(self.project_dir / "config.ini"),
                env_path=str(self.project_dir / ".env")
            )
            self.config = loader.load_configs()
            print("✓ Configuration loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load configuration: {e}")
            sys.exit(1)

    def check_modal_installed(self) -> bool:
        """Check if Modal CLI is installed."""
        try:
            result = subprocess.run(
                ["modal", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def check_modal_authenticated(self) -> bool:
        """Check if Modal is authenticated."""
        try:
            result = subprocess.run(
                ["modal", "volume", "list"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install_modal(self):
        """Install Modal CLI."""
        print("\n" + "=" * 60)
        print("📦 INSTALLING MODAL CLI")
        print("=" * 60)

        if self.check_modal_installed():
            print("✓ Modal is already installed")
            return

        print("Installing Modal...")
        try:
            subprocess.run(
                ["pip", "install", "modal"],
                check=True
            )
            print("✓ Modal installed successfully")
        except subprocess.CalledProcessError:
            print("✗ Failed to install Modal")
            sys.exit(1)

    def authenticate_modal(self):
        """Authenticate with Modal."""
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATING WITH MODAL")
        print("=" * 60)

        if self.check_modal_authenticated():
            print("✓ Modal is already authenticated")
            return

        print("Opening browser for authentication...")
        print(f"Manually run 'modal setup' if the browser does not open automatically.")
        try:
            subprocess.run(["modal", "setup"], check=True)
            print("✓ Modal authentication successful")
        except subprocess.CalledProcessError:
            print("✗ Modal authentication failed")
            sys.exit(1)

    def create_volume(self):
        """Create persistent volume on Modal."""
        print("\n" + "=" * 60)
        print("💾 CREATING PERSISTENT VOLUME")
        print("=" * 60)

        volume_name = self.config["filesystem"]["volume_name"]
        print(f"Creating volume: {volume_name}")

        try:
            result = subprocess.run(
                ["modal", "volume", "create", volume_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 or "already exists" in result.stderr:
                print(f"✓ Volume '{volume_name}' ready")
                return True
            else:
                print(f"✗ Failed to create volume: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error creating volume: {e}")
            return False

    def setup_folder_structure(self):
        """Create folder structure in the persistent volume."""
        print("\n" + "=" * 60)
        print("📁 SETTING UP FOLDER STRUCTURE")
        print("=" * 60)

        volume_name = self.config["filesystem"]["volume_name"]
        folders = [
            "checkpoints",
            "text_encoders",
            "diffusion_models",
            "embeddings",
            "loras",
            "unet",
            "vae",
            "model_patches",
            "custom_nodes",
            "output"
        ]

        print(f"Creating folder structure in '{volume_name}'... will take a moment.")

        for folder in folders:
            try:
                # Create folder using modal volume with a simple touch command
                subprocess.run(
                    #modal volume put my-comfy-models ./.emptyfile YOYOYOYO1234/
                    ["modal", "volume", "put", f"{volume_name}", 
                     "./.emptyfile", f"{folder}/"],
                    capture_output=True,
                    check=False
                )
                print(f"  ✓ {folder}/")
            except Exception as e:
                print(f"  ✗ Failed to create {folder}: {e}")

        print("✓ Folder structure created")

    def download_models(self):
        """Download essential models from Hugging Face."""
        print("\n" + "=" * 60)
        print("🤖 DOWNLOADING MODELS (OPTIONAL)")
        print("=" * 60)
        print("Model downloading is disabled by default to save setup time.")
        print(f"Drop into your Modal volume's shell using:")
        print(f"    modal shell --volume {self.config['filesystem']['volume_name']}")
        print(f"and then use \"wget\" utility to download models manually.")
        print(f"Alternatively, you can use the 'modal volume put' command to upload models from your local machine to the volume.")
        print(f"Do not forget to run \"sync\" command inside volume's shell after downloading models to ensure they are properly saved in the volume.")
        input("Press Enter to continue...")
        return
        print("Model downloading from Hugging Face can be time-consuming.")
        response = input("Do you want to download essential models now? (y/n): ").strip().lower()

        if response != 'y':
            print("Skipping model download. You can download them later manually.")
            return

        hf_token = self.config["tokens"].get("hf_token")
        if not hf_token or hf_token == ".env":
            print("⚠ Hugging Face token not configured. Skipping model download.")
            return

        # Example models (customize as needed)
        models = [
            # "black-forest-labs/FLUX.1-dev",  # Large model, requires authentication
            # "stabilityai/stable-diffusion-3-medium",
            # Add more models as needed
        ]

        if not models:
            print("No models configured for download.")
            print("You can manually download models using:")
            print("  huggingface-cli download <model-id> --local-dir ./checkpoints")
            return

        print("Note: Model downloading is disabled by default to save setup time.")
        print("Download models manually when needed:")
        for model in models:
            print(f"  huggingface-cli download {model} --local-dir ./checkpoints")

    def generate_yaml_config(self):
        """Generate extra_model_paths.yaml from config.ini"""
        if self.project_dir / "extra_model_paths.yaml".exists():
            print("\n" + "=" * 60)
            print("⚙️  YAML CONFIGURATION ALREADY EXISTS")
            print("=" * 60)
            print("✅ extra_model_paths.yaml already exists, skipping generation.")
            return
        print("\n" + "=" * 60)
        print("⚙️  GENERATING YAML CONFIGURATION")
        print("=" * 60)

        try:
            output_file = self.project_dir / "extra_model_paths.yaml"
            generate_extra_model_paths(
                config_file=str(self.project_dir / "config.ini"),
                output_file=str(output_file)
            )
            print(f"✓ Generated {output_file.name}")
        except Exception as e:
            print(f"✗ Failed to generate YAML configuration: {e}")
            sys.exit(1)

    def setup_env_file(self):
        """Setup .env file from .env.BAK template."""
        print("\n" + "=" * 60)
        print("🔑 SETTING UP ENVIRONMENT VARIABLES")
        print("=" * 60)

        env_file = self.project_dir / ".env"
        env_bak_file = self.project_dir / ".env.BAK"

        if env_file.exists():
            print("✓ .env file already exists")
            return

        if env_bak_file.exists():
            print("Creating .env from .env.BAK template...")
            shutil.copy(env_bak_file, env_file)
            print("✓ .env file created")
            print("\n⚠️  IMPORTANT: Edit .env file with your actual tokens:")
            print(f"  {env_file}")
            return

        # Create a template .env file if .env.BAK doesn't exist
        template_content = """# Rename this file to .env and keep it private
# Paste your tokens here

# Hugging Face API Token (get from https://huggingface.co/settings/tokens)
HF_TOKEN = "your_hf_token_here"

# CivitAI API Token (get from https://civitai.com/user/account)
CIVITAI_API_TOKEN = "your_civitai_token_here"
"""
        env_file.write_text(template_content)
        print("✓ .env template created")
        print("\n⚠️  IMPORTANT: Edit .env file with your actual tokens:")
        print(f"  {env_file}")

    def verify_setup(self):
        """Verify that all setup steps completed successfully."""
        print("\n" + "=" * 60)
        print("✅ VERIFYING SETUP")
        print("=" * 60)

        checks = [
            ("Modal CLI", self.check_modal_installed()),
            ("Modal Authentication", self.check_modal_authenticated()),
            (".env file", (self.project_dir / ".env").exists()),
            ("config.ini", (self.project_dir / "config.ini").exists()),
            ("extra_model_paths.yaml", (self.project_dir / "extra_model_paths.yaml").exists()),
        ]

        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"{status} {check_name}")
            if not result:
                all_passed = False

        return all_passed

    def print_next_steps(self):
        """Print next steps for the user."""
        print("\n" + "=" * 60)
        print("🎉 SETUP COMPLETE!")
        print("=" * 60)

        print("\n📋 Next Steps:")
        print("\n1. Edit your configuration (optional):")
        print(f"   {self.project_dir / 'config.ini'}")

        print("\n2. Edit environment variables (IMPORTANT):")
        print(f"   {self.project_dir / '.env'}")
        print("   Add your Hugging Face and CivitAI tokens")

        print("\n3. Download custom nodes (optional):")
        print("   Visit https://registry.comfy.org to find and clone nodes")
        print("   Place them in your Modal volume's custom_nodes/ folder")

        print("\n4. Download models (optional):")
        print("   Place .safetensors, .ckpt, or .gguf files in appropriate folders")
        print("   Upload to Modal volume using:")
        print(f"   modal volume put {self.config['filesystem']['volume_name']} <local-path> <remote-path>")
        print(f"   OR   ")
        print(f"Drop into volume shell:")
        print(f"   modal shell --volume {self.config['filesystem']['volume_name']}")
        print(f"cd to /mnt/{self.config['filesystem']['volume_name']}/diffusion_models/ (or other folders)")
        print("   Use wget or curl to download models directly into the volume")
        print("   Don't forget to run 'sync' command inside the shell after downloading")

        print("\n5. Start ComfyUI:")
        print("   modal serve main.py")

        print("\n📚 Documentation:")
        print("   - 🚀 Modal × ComfyUI: https://github.com/Renks/MxC")
        print("   - Modal: https://modal.com/docs")
        print("   - ComfyUI: https://github.com/Comfy-Org/ComfyUI")
        print("   - ComfyUI Registry: https://registry.comfy.org")

        print("\n💡 Tips:")
        print("   - Use 'modal logs --app <app-name>' to view logs")
        print("   - Use 'modal volume ls <volume-name>' to browse your volume")
        print("   - Use './browsefs.sh' to access container shell")

    def run(self):
        """Run the complete setup process."""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "  🚀 Modal × ComfyUI Setup Script".center(57) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        try:
            # Step 1: Install Modal
            self.install_modal()

            # Step 2: Authenticate with Modal
            self.authenticate_modal()

            # Step 3: Create volume
            self.create_volume()

            # Step 4: Setup folder structure
            self.setup_folder_structure()

            # Step 5: Download models (optional)
            self.download_models()

            # Step 6: Generate YAML config
            self.generate_yaml_config()

            # Step 7: Setup .env file
            # self.setup_env_file() # Already called in load_config if missing

            # Step 8: Verify setup
            if self.verify_setup():
                self.print_next_steps()
            else:
                print("\n⚠️  Some checks failed. Please review the output above.")
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    setup = ModalSetup()
    setup.run()


if __name__ == "__main__":
    main()