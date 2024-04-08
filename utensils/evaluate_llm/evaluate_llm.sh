#!/usr/bin/env bash
# Compare multiple models by running them with the same questions based on user input

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to exit with a message
exit_with_message() {
    printf "${RED}%s${NC}\n" "$1" >&2
    exit 1
}

# Check for correct usage
if [ "$#" -ne 2 ]; then
    exit_with_message "Usage: $0 <number of models> <request file path>"
fi

# Validate number of models input
if ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -le 0 ]; then
    exit_with_message "The number of models must be a positive integer."
fi

NUMBEROFCHOICES=$1

# Check if the question file exists and is readable
if [ ! -f "$2" ] || [ ! -r "$2" ]; then
    exit_with_message "$2 not found or is not readable. Please make sure the file exists and is readable."
fi

REQUEST_CONTENT=$(<"$2")

# Retrieve model list
CHOICES=$(ollama list | awk '{print $1}' 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$CHOICES" ]; then
    exit_with_message "Failed to retrieve model list or no models available."
fi

SELECTIONS=()
declare -a SUMS=()
COUNT=0

printf "${GREEN}Select $NUMBEROFCHOICES models to compare:${NC}\n"
select ITEM in $CHOICES; do
    if [[ -n $ITEM ]]; then
        printf "${YELLOW}You have selected $ITEM${NC}\n"
        SELECTIONS+=("$ITEM")
        ((COUNT++))
        if [[ $COUNT -eq $NUMBEROFCHOICES ]]; then
            break
        fi
    else
        printf "${RED}Invalid selection. Please try again.${NC}\n"
    fi
done

printf "\n${YELLOW}-@@@-${NC}\n"
for ITEM in "${SELECTIONS[@]}"; do
    printf "${YELLOW}--------------------------------------------------------------${NC}\n"
    printf "Selecting the model ${GREEN}$ITEM${NC}\n"
    if ! ollama run "$ITEM" ""; then
        printf "${RED}Failed to load model $ITEM. Skipping...${NC}\n"
        continue
    fi
    printf "${YELLOW}--------------------------------------------------------------${NC}\n"
    printf "Running the request ---${RED}$REQUEST_CONTENT${NC}--- with the model ${GREEN}$ITEM${NC}\n"

    if COMMAND_OUTPUT=$(ollama run "$ITEM" --verbose < "$2" 2>&1 | tee /dev/stderr); then
        SUM=$(echo "$COMMAND_OUTPUT" | awk '/eval duration:/ {
        value = $3
        if (index(value, "ms") > 0) {
            gsub("ms", "", value)
            value /= 1000
        } else if (index(value, "m") > 0) {
            gsub("m", "", value)
            value *= 60
        } else {
            gsub("s", "", value)
        }
        sum += value
    }
    END { print sum }')


        SUMS+=("The request for $ITEM completed in $SUM seconds")
    else
        printf "${RED}An error occurred while running the model $ITEM. Skipping...${NC}\n"
    fi
done

printf "\n${YELLOW}--------------------------------------------------------------${NC}\n"
printf "\n${GREEN}Request evaluation for each run:${NC}\n"
for val in "${SUMS[@]}"; do
    printf "%s\n" "$val"
done

printf "\n${YELLOW}--------------------------------------------------------------${NC}\n"
printf "\n${GREEN}LLMs comparison complete for request: \"%s\"${NC}\n" "$REQUEST_CONTENT"
printf "\n${YELLOW}--------------------------------------------------------------${NC}\n"
printf "\n${YELLOW}-@@@-${NC}\n"
printf "\n${YELLOW} Evaluate the results above with LLM Examiner at: ${NC}\n"
printf "\n${YELLOW} https://chat.openai.com/g/g-WaEKsoStj-llm-examiner ${NC}\n"

printf "\n${YELLOW}--------------------------------------------------------------${NC}\n"