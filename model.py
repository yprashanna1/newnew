import json
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Initialize the GPT-Neo 2.7B model
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def load_rules(file_path='rules.json'):
    """
    Load ethical rules from a JSON file.
    """
    with open(file_path, 'r') as file:
        rules_data = json.load(file)
    return rules_data

def save_rules(rules_data, file_path='rules.json'):
    """
    Save ethical rules to a JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(rules_data, file, indent=4)

def get_ai_response(prompt):
    """
    Generate AI response using the GPT-Neo model.
    """
    response = generator(
        prompt,
        max_length=150,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        truncation=True
    )[0]['generated_text']
    return response

def check_response_against_rules(response, rules_data):
    """
    Check if the AI response adheres to the ethical rules.
    """
    response_lower = response.lower()
    for category, rules in rules_data.items():
        for rule_set in rules:
            if any(keyword.lower() in response_lower for keyword in rule_set['query_keywords']):
                for rule in rule_set['rules']:
                    if not re.search(re.escape(rule.lower()), response_lower):
                        return False, rule
    return True, ""

def request_modified_response(prompt, missing_rule):
    """
    Request a modified AI response that adheres to the missing rule.
    """
    modified_prompt = f"{prompt}\nPlease refine your answer according to this rule: {missing_rule}"
    response = get_ai_response(modified_prompt)
    return response

def add_rule(category, query_keywords, new_rules, rules_data):
    """
    Add a new set of rules under a specific category.
    """
    if category not in rules_data:
        rules_data[category] = []
    rules_data[category].append({
        "query_keywords": query_keywords,
        "rules": new_rules
    })
    save_rules(rules_data)
    print(f"Rule added successfully under category '{category}'.")
