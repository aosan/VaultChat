# LLM Performance Comparison Tool

## Overview
This script facilitates the comparison of multiple LLMs by running requests through each selected model and measuring their performance. It is designed to help you compare and evaluate the capabilities and response times of your models or Modelfile fine-tuning in processing an identical request.

## Prerequisites
- Bash shell environment
- `ollama` installed and configured on your system

## Usage
```bash
./evaluate_llm.sh <number of models> <request file path>
```

Where:
- `<number of models>` is the number of models you wish to compare
- `<request file path>` is the path to a file containing the request

### Example
```bash
./evaluate_llm.sh 3 evaluate_marketing.txt
```

This will select 3 models from your available LLMs and make a request with the contents of `evaluate_marketing.txt` to each selected model.

## Outcome
The script displays:
- The response from each selected model.
- The evaluation durations for each model.
- A direct link to [LLM Examiner](https://chat.openai.com/g/g-WaEKsoStj-llm-examiner) for further analysis of the results.

Copy-paste the complete output between -@@@- to the LLM Examiner for an evaluation and a 1 to 10 score for each model's accuracy, completeness, clarity, responsiveness and efficiency.

## Note
Ensure `ollama` is correctly installed and you have access to the models you wish to compare.

For more information on the `ollama` usage and models, please visit [ollama](https://github.com/ollama/ollama).

## License
This software is released under the AGPL-3.0 license.
