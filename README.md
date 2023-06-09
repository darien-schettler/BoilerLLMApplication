# Project Name: LLM-Hosting-Boilerplate

LLM-Hosting-Boilerplate is a Python project designed to facilitate the hosting of Large Language Models (LLMs) with ease. It is flexible enough to allow users to host different types of LLMs (Bring your own model, Hugging Face models, etc.) on multiple cloud service platforms (AWS, GCP, Azure, or own server) powered by the Runhouse library.

---

## Project Directory Structure

```
BoilerLLMApplication/
|
|---- LICENSE
|---- README.md
|---- requirements.txt
|
|---- src/
|     |---- __init__.py
|     |
|     |---- config/
|     |     |---- __init__.py
|     |     |---- settings.py
|     |
|     |---- model_manager/
|     |     |---- __init__.py
|     |     |---- model_loader.py
|     |     
|     |-- runhouse_ops/
|     |     |---- __init__.py
|     |     |---- instance_handler.py
|     |
|     |---- server/
|     |     |---- __init__.py
|     |     |---- app.py
|     |
|     |---- data_manager/
|     |     |---- __init__.py
|     |     |---- data_loader.py
|     |
|     |---- monitoring/
|     |     |---- __init__.py
|     |     |---- logger.py
|     
|---- examples/
|     |---- example_01.py
|     |---- ...
|     |---- example_xx.py
|     
|---- docs/
|     |---- index.md
|     |---- setup_guide.md
|     |---- model_addition_guide.md
|    
```

### Module Breakdown

- **`config`:** This module handles all the configuration settings for the LLMs and the deployment environment.
- **`model_manager`:** This module manages the loading of models from various sources (Hugging Face, custom models, etc.).
- **`runhouse_ops`:** This module leverages the capabilities of Runhouse to launch, configure, and terminate instances on the cloud platforms.
- **`server`:** This module contains a server (like Flask or FastAPI) to handle incoming requests and return predictions from the LLM.
- **`data_manager`:** This module handles fetching and managing any data resources required by the LLM.
- **`monitoring`:** This module is responsible for tracking performance and resource utilization of the instances.

---

## Getting Started

1. Clone the repository: 
```bash
git clone https://github.com/darien-schettler/BoilerLLMApplication.git
```

2. Install the requirements: 
```bash
pip install -r requirements.txt
```

3. Configure your deployment environment and model settings in **`config/settings.py`**.

4. Start your server (more instructions in **`docs/setup_guide.md`**).

For more detailed instructions and guides, refer to the **`docs/`** folder.

---

## Contribution

We welcome contributions to this project. Please feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or support, please contact darien_schettler@hotmail.com

---

## Acknowledgements

This project utilizes the Runhouse library for managing cloud resources and was largely developed with their support and guidance.