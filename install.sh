#!/usr/bin/env sh

# Utility functions
vergte() {
   printf '%s\n%s' "$2" "$1" | sort -C -V
}

read_input() {
  read -r -p "$1" response
  # Set default response to "Y", why not
  response=${response:-Y}
  printf "%s" "$response"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Initial checks before takeoff
# Check for a supported Ollama version
if ! command_exists ollama; then
  printf "\n >>> Ollama not found. Please (re)install it from 'https://ollama.com/download'\n"
  exit 1
fi

OLLAMA_VER=$(ollama --version | grep -oE '[0-9]+(\.[0-9]+)+')
if ! vergte "$OLLAMA_VER" "0.1.30"; then
  printf "\n >>> Ollama version too old. Please update to 0.1.30 or higher.\n"
  exit 1
fi

# figure out pyenv
if ! command_exists pyenv; then
  printf "\n >>> Pyenv not found.\n"
  response=$(read_input " >>> Would you like to install pyenv? [Y/n]: ")
  
  response=${response:-Y}
  
  case "$response" in
    [yY][eE][sS]|[yY])
      printf ">>> Installing pyenv...\n"
      curl https://pyenv.run | bash
      ;;
    *)
      printf "\n >>> Installation is stopped. Exiting...\n"
      exit 1
      ;;
  esac
else
  printf "\n >>> Pyenv is already installed.\n"
fi

# 3. Update shell configuration for pyenv, if needed. Don't ask me why.
if [ "$response" = "Y" ] || [ "$response" = "y" ]; then
  PATH_MODIFICATION='export PATH="$HOME/.pyenv/bin:$PATH"'
  if ! printf $PATH | grep -q "$HOME/.pyenv/bin"; then
    if [ -n "$FISH_VERSION" ]; then
      printf "set -gx PATH $HOME/.pyenv/bin \$PATH\n" >> ~/.config/fish/config.fish
    else
      printf "$PATH_MODIFICATION\n" >> ~/$([ -n "$ZSH_VERSION" ] && echo ".zshrc" || echo ".bashrc")
    fi
  fi
  
  if [ -z "$FISH_VERSION" ]; then
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
  fi

  printf ">>> pyenv installed successfully.\n"
  printf ">>> Please restart your shell session or source your shell configuration file for the changes to take effect.\n"
fi

# Install and setup Python version, without animal control support
if ! pyenv versions | grep -q '3.12'; then
  pyenv install 3.12
fi

pyenv local 3.12

if ! pyenv version | grep -q '3.12'; then
  printf "\n >>> Python 3.12 not found. Please install it manually with pyenv install 3.12 \n"
  exit 1
fi

# Install Python dependencies from the deepest circle of hell, just ask Dante Alighieri
pip install -r requirements.txt

# .env file setup for the VaultChat centre of the universe
if [ ! -f ".env" ]; then
  printf " >>> The .env file does not exist."
  response=$(read_input " >>> Would you like to create it from .env.example? [Y/n]:")
  
  if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    cp .env.example .env
    printf "\n >>> Please adjust the variables in .env file to your needs.\n"
  else
    printf "Skipping .env file creation.\n"
  fi
fi


# Setup private documents directory, Mr. Lawyer
printf "\n Private Documents Location:\n"
grep SOURCE_DIRECTORY .env
read_input ">>> Enter a new path for private documents (leave blank to use default): " response

if [ -n "$response" ]; then
  printf "\n >>> Setting Private Documents Location: $response \n"
  sed "s|SOURCE_DIRECTORY=.*|SOURCE_DIRECTORY=$response|" .env > .env.tmp && mv .env.tmp .env
else
  printf "\n Using default Private Documents Location.\n"
fi

# Make them run
chmod +x docs_loader.py vaultChat.py

# Final instructions for smart and good looking customers
printf "\n >>> Installation was successful!\n"
printf "\n >>> Run './docs_loader.py' to prepare your private data.\n"
printf "\n >>> Important! Run './docs_loader.py' again every time you change documents in the $SOURCE_DIRECTORY directory.\n"
printf "\n >>> Run './vaultChat.py' to start the application after your private data store creation or update.\n"

# That's all, folks
exit 0
