import requests
import os


# Configuracao de constantes.
API_TOKEN = os.getenv("API_KEY")
if not API_TOKEN:
    print("API nao setada")
    exit()
    
HEADERS = {
"Authorization": f"Bearer {API_TOKEN}",
"Content-Type": "application/json"
}

def getting_tests():
    
    API_URL = 'https://.../aeb0e0e4-e61b-429a.../edit?channelId=61eeb5d3-fc0a...'
    
    response = requests.get(API_URL, headers=HEADERS)
    data = response.json()
    
    return data

def deep_search_for_question_text(interaction_data):
    """Performs a deep search within interaction data to find the question text."""
    if "question" in interaction_data and "interactions" in interaction_data["question"]:
        for sub_interaction in interaction_data["question"]["interactions"].values():
            if sub_interaction.get("type") == "TEXT" and "html" in sub_interaction.get("data", {}):
                return sub_interaction["data"]["html"]
    return "Question not provided"


def extract_questions_and_answers(interactions_data):
    questions_answers = []
    
    for interaction_id, interaction_data in interactions_data.items():
        # Check if the content is in Portuguese
        content_language = interaction_data.get("taskGroup", {}).get("properties", {}).get("contentLanguage")
        
        if content_language == "pt_BR":
            # Extract question text (or use a placeholder if missing)
            question_data = interaction_data.get("tasks", {}).get("question", {}).get("interactions", {})
            print(question_data)
            # Search for the string preceding "data" and extract question text
            question_text = ""
            for interaction_key, interaction_value in question_data.items():
                
                if "data" in interaction_value and "html" in interaction_value["data"]:
                    question_text = question_data[interaction_key - 1]["data"]["text"]
                    break
            if not question_text:
                question_text = "Question not provided"
            
            # Extract options and correct answer from the interaction within tasks
            answer_data = interaction_data.get("tasks", {})
            answer_task_id_list = interaction_data.get("taskGroup", {}).get("structure", {}).get("taskOrder", [])
            
            if not answer_task_id_list:
                continue
            
            answer_task_id = answer_task_id_list[0]
            answer_interaction_data = answer_data.get(answer_task_id, {}).get("interaction", {}).get("interactions", {})
            
            options_data = next((v.get("data", {}) for k, v in answer_interaction_data.items() if v.get("type") == "MC"), {})
            
            options_texts = [answer_interaction_data.get(option_id, {}).get("data", {}).get("html") for option_id in options_data.get("options", [])]
            correct_answer_ids = options_data.get("correctAnswersIds", [])
            
            if not correct_answer_ids:
                continue
            
            correct_answer_id = correct_answer_ids[0]
            correct_answer_text = answer_interaction_data.get(correct_answer_id, {}).get("data", {}).get("html")
            
            if options_texts and correct_answer_text:
                questions_answers.append({
                    "question": question_text,
                    "options": options_texts,
                    "answer": correct_answer_text
                })

                    
    return questions_answers
    
    
data = getting_tests()
# print(data)
questions_answers = extract_questions_and_answers(data.get('pages', {}).get('interactions', {}))


for qa in questions_answers:
    print(f"Question: {qa['question']}")
    print(f"Options: {', '.join(qa['options'])}")
    print(f"Answer: {qa['answer']}\n")
    
    