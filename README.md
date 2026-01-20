# AgentsFactory
## Project Initialization & Setup Guide

### 1. Installation
Install the package directly from the GitHub repository:

```bash
pip install git+https://github.com/YehudaWieder/AgentsFactory.git
```

### 2. Project Initialization
Run the following commands to initialize your project folder with the necessary configuration files and directory structure:

#### Clone only the necessary templates using sparse-checkout
```powershell
git clone --no-checkout --depth 1 --filter=blob:none https://github.com/YehudaWieder/AgentsFactory.git temp-repo
cd temp-repo
git sparse-checkout init --cone
git sparse-checkout set agents_factory/templates/user_data agents_factory/templates/run_pipeline.py
git checkout
cd ..
```

### Move templates to your project root (Linux/macOS syntax)
```bash
mv temp-repo/agents_factory/templates/user_data ./user_data
mv temp-repo/agents_factory/templates/run_pipeline.py ./run_pipeline.py
```

### Move templates to your project root (windows)
```powershell
Move-Item -Path "temp-repo\agents_factory\templates\user_data" -Destination ".\user_data" -Force
Move-Item -Path "temp-repo\agents_factory\templates\run_pipeline.py" -Destination ".\run_pipeline.py" -Force
```

### Cleanup temporary files (Linux/macOS syntax)
```bash
rm -rf temp-repo
```

### Cleanup temporary files (windows)
```powershell
Remove-Item -Path "temp-repo" -Recurse -Force
```

---

### 3. Setup and Customization

### —

#### 3.1 Customize the core behavior of your factory by editing the `user_data/config.py` file. This file manages paths and security constraints.

   **Essential Settings:**
  
   - **ENV_PATH:** Path to your environment variables file (e.g., API_keys.env).
  
   - **AGENT_CONFIG_DEFAULT_PATH:** Path to the YAML file defining your agents.
  
   - **CUSTOM_TOOLS_PATH:** Path to the Python file containing your custom tool definitions.
  
   - **MAX_FILE_SIZE:** Sets the maximum allowed file size for processing (Default: 100 KB).
  
   - **MAX_NESTING_DEPTH:** Limits the recursion depth for complex agent tasks (Default: 20).

### —

#### 3.2 You need to set up your credentials in the `user_data/API_keys.env` file. This file stores the keys required for the models and tracking services.

   **Key Requirements:**
  
   - **Model Keys**: You must define a key for every model provider you plan to use. For example, populate `OPENAI_API_KEY` for OpenAI models or `ANT_API_KEY` for Anthropic models.
  
   - **Langfuse Setup**: To monitor and trace your agents' performance, you must provide your `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`.
  
   - **Monitoring Path**: Set the `LANGFUSE_HOST` (e.g., `https://cloud.langfuse.com`) to ensure your logs are sent to the correct dashboard.

### —

#### 3.3 Extend your agents' capabilities by defining unique functions and registering them in the factory. Define your logic in `user_data/custom_tools/custom_tools.py` and update the registry.

   **Tool Implementation:**
  
   - **Create Functions**: Write your custom Python functions in `custom_tools.py`. These can be any logic or external API calls your agents need.

   - **Register Tools**: After defining a function, you **must** add it to the `CUSTOM_TOOLS_REGISTRY` in `tools_registry.py`.
  
   - **Mapping**: Ensure the dictionary key in the registry matches the name the agent will use to call the tool.
  
   - **Importing**: Don't forget to import your new function from `custom_tools.py` into `tools_registry.py` so the factory can recognize it.

### —

#### 3.4 This file `agent_config.yaml` or `agent_config.json` defines the heart of your factory: the prompts, tools, agents, and the execution flow (pipeline).

 **Agent Configuration:**

 **Prompts**:
   - Define the prompts to be pulled from **Langfuse**.
   - **Requirement**: Any prompt assigned to an agent **must** first be declared in this `prompts` section.

 **Tools**:
   - List all available functions or utilities.
   - **ref**: This must match the name in your `tools_registry.py`.
   - **Requirement**: Any tool assigned to an agent **must** first be registered in this `tools` section.

**Agents**:
   - You can define **as many agents as you need** to handle complex workflows.
   - **model**: Specify provider and model (e.g., `openai:gpt-4o-mini`).
   - **tools**: A list of tools available to this agent. 
     - *Note*: You can include other agents here, allowing them to collaborate.
   - **prompt**: The identifier for the system prompt.
   - **output_format**: Determines the response type (e.g. `str`, `json` or `raw`).

 **Pipeline**:
   - Defines the execution sequence. This is where the factory starts processing your request by calling the specified agents in order.

---

### 5. Execution and Implementation
The `run_pipeline.py` script is the main entry point for interacting with your agents. It handles the initialization of the factory and executes the logic you defined.

**How to use:**

* **Path Initialization (Critical)**: Before importing the factory components, you must initialize the `user_data` path to ensure the system points to your local tools and configurations. This is done by passing your absolute path to `get_user_data(base_path=...)`.

* **Running the Factory**: Simply execute the script to start an interactive session. You can send prompts to your pipeline and receive processed results in real-time.

* **Switching Configurations**: You are not limited to one setup. You can maintain multiple `config` files for different tasks and load them by passing the file path:
  `pipeline = create_pipeline(config_path="user_data/your_custom_config.yaml")`

* **External Integration**: You can import `create_pipeline` into other Python scripts. This allows you to use your agentic workflow as a modular component within any larger application.

* **Tracing**: The script is pre-configured to flush logs to Langfuse, ensuring that every interaction is recorded for monitoring and debugging.
