
<h1 align="center">
  <a href="https://github.com/aosan/VaultChat">
    <img src="https://github.com/aosan/VaultChat/blob/main/static/VaultChat_logo.png" width="128" height="128" alt="VaultChat"/>
  </a><br>
  VaultChat
</h1>

# VaultChat

Are you concerned about the cybersecurity and privacy risks of sharing sensitive or private documents when using AI? Public AI is a threat to your privacy and cybersecurity.

We understand how crucial your privacy is when discussing sensitive matters and sharing confidential documents. The thought of your private conversations or documents falling into the wrong hands is panic inducing on a good day.

VaultChat keeps all your chats and documents private. No query or document leaves your computer.

What happens in VaultChat, stays in VaultChat.

## Description
Chat privately with your documents and a local language model.

## Installation on Linux
Install Ollama from https://www.ollama.com

Configure and deploy your desired LLM, mistral is a good first choice.

```Bash
ollama pull mistral
```

VaultChat is tested on Linux only, in Preview for MacOS and Windows.

Consult `.env.example` and copy the `.env.example` file to `.env` and update the configuration 

Ensure you have Python 3.12 and pyenv installed on your Linux or MacOS. Then, go to the release package and run:

```Bash
chmod +x install.sh && ./install.sh
```

## Installation on Windows
- Install Microsoft Visual C++ 14 or greater, get it with "Microsoft C++ Build Tools" from https://visualstudio.microsoft.com/visual-cpp-build-tools/ and install Visual Studio Build Tools 2022 and Visual Studio Community 2022.
- Install pyenv from https://pypi.org/project/pyenv-win/#power-shell and follow all the installation steps.
- Install Python 3.12 with pyenv:

```powershell
pyenv.bat install 3.12
```

- Install VaultChat dependencies from the release package and run:

```powershell
pip.bat install -r requirements
```

## Usage
### Load Private Documents

Copy your private documents to `private_documents` and create the embeddings:

Linux
```Bash
./docs_loader.sh
```

Windows
```powershell
python.bat docs_loader.sh
```

Run `docs_loader.sh` every time you add or remove documents in private_documents.

Remove `chroma_db` directory with your embeddings every time you wish to change the embeddings model configuration or chat with a new set of private documents.

### VaultChat with your Private Documents

After your embeddings have been created, start a chat:

Linux
```Bash
./vaultChat.py
```

Windows
```powershell
python.bat vaultChat.py
```

Type `/bye` or `exit` to finish the chat

## Requirements
- Minimum hardware requirements: Ollama baseline. If your system can run Ollama, it can run VaultChat.
- Ollama with models installed, choice of model to be defined in `.env`
- Python 3.12
- pyenv
- Dependencies as listed and installed from `requirements.txt`.

## Contributions
Contributions are welcomed!
Please create a PR with a single typo/issue/defect/feature.

## Roadmap
VaultChat started as a week-end experimental project with the objective of learning the LLM ecosystem.

The early releases are focused on bug fixes and usability improvements. It will remain a console version until features and functionality have matured.

GUI and web interfaces will be provided at a later stage.

## Support
VaultChat is an experimental project. Support is provided on a "best effort" basis.

## Utensils
Use the tools in the `utensils` directory to assist with your use of VaultChat.

`epub2md` will convert an EPUB document to Markdown for a faster and more efficient embeddings creation.

`pdf2md` will convert a PDF document to Markdown for a faster and more efficient embeddings creation.

`evaluate_llm` will help you fine-tune your selection of ollama models and any other model fine-tuning.

## License
This software is released under the AGPL-3.0 license.

## Credit
Private LLMs made easy with Ollama https://www.ollama.com

Support for local LLMs with LangChain https://python.langchain.com

PromptEngineer48 for the ingestion and retrieval inspiration https://github.com/PromptEngineer48/Ollama

Personal Vault Project by Lucian https://github.com/dlucian/pvp

NLP journey started with Norbert Z.
