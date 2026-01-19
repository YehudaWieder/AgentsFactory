# AgentsFactory
## Project Initialization & Setup Guide

### 1. Installation
Install the package directly from the GitHub repository:

```bash
pip install git+[https://github.com/YehudaWieder/AgentsFactory.git](https://github.com/YehudaWieder/AgentsFactory.git)
```

### 2. Project Initialization
Run the following commands to initialize your project folder with the necessary configuration files and directory structure:

```powershell
# Clone only the necessary templates using sparse-checkout
git clone --no-checkout --depth 1 --filter=blob:none [https://github.com/YehudaWieder/AgentsFactory.git](https://github.com/YehudaWieder/AgentsFactory.git) temp-repo
cd temp-repo
git sparse-checkout init --cone
git sparse-checkout set agents_factory/templates/user_data agents_factory/templates/run_pipeline.py
git checkout
cd ..
```

# Move templates to your project root (Linux/macOS syntax)
```bash
mv temp-repo/agents_factory/templates/user_data ./user_data
mv temp-repo/agents_factory/templates/run_pipeline.py ./run_pipeline.py
```

# Move templates to your project root (windows)
```powershell
Move-Item -Path "temp-repo\agents_factory\templates\user_data" -Destination ".\user_data" -Force
Move-Item -Path "temp-repo\agents_factory\templates\run_pipeline.py" -Destination ".\run_pipeline.py" -Force
```

# Cleanup temporary files (Linux/macOS syntax)
```bash
rm -rf temp-repo
```

# Cleanup temporary files (windows)
```powershell
Remove-Item -Path "temp-repo" -Recurse -Force
```

---

### 3. Setup and Customization
After running the initialization script, you can now customize your project by modifying the files in the `user_data` directory to match your specific agent logic and tools.