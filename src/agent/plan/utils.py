import re

def extract_plan(response):
    extracted_data = {}
    # Clean response from code blocks if present
    clean_response = re.sub(r'```[a-zA-Z]*\n?', '', response)
    clean_response = re.sub(r'```', '', clean_response)
    
    # Check if it's Option 1 (gathering information) - more flexible regex
    option1_match = re.search(r'<option>.*?<question>(.*?)</question>.*?<answer>(.*?)</answer>.*?<route>(.*?)</route>.*?</option>', clean_response, re.DOTALL | re.IGNORECASE)
    if option1_match:
        extracted_data['Question'] = option1_match.group(1).strip()
        extracted_data['Answer'] = option1_match.group(2).strip()
        extracted_data['Route'] = option1_match.group(3).strip()
        return extracted_data

    # Check if it's Option 2 (providing the final plan) - more flexible regex
    option2_match = re.search(r'<option>.*?<plan>(.*?)</plan>.*?<route>(.*?)</route>.*?</option>', clean_response, re.DOTALL | re.IGNORECASE)
    if option2_match:
        # Extract each task from the plan
        plan_content = option2_match.group(1).strip()
        # Supporting multiple task formats (1. Task, - Task, * Task)
        tasks = re.findall(r'(?:\d+\.|\-|\*)\s*(.*)', plan_content)
        if not tasks:
            # Fallback for just lines
            tasks = [line.strip() for line in plan_content.split('\n') if line.strip()]
        
        extracted_data['Plan'] = [t.strip() for t in tasks if t.strip()]
        extracted_data['Route'] = option2_match.group(2).strip()
        return extracted_data
    
    return None

def extract_llm_response(xml_response: str) -> dict:
    # Initialize the result dictionary
    result = {
        'Current Plan': None,
        'Pending': [],
        'Completed': [],
        'Final Answer': None,
        'Route': None
    }
    
    # Clean response from code blocks if present
    clean_response = re.sub(r'```[a-zA-Z]*\n?', '', xml_response)
    clean_response = re.sub(r'```', '', clean_response)

    # Define regex patterns to match each part of the response
    current_plan_regex = re.compile(r'<current-plan>\s*(.*?)\s*</current-plan>', re.DOTALL | re.IGNORECASE)
    pending_regex = re.compile(r'<pending>\s*(.*?)\s*</pending>', re.DOTALL | re.IGNORECASE)
    completed_regex = re.compile(r'<completed>\s*(.*?)\s*</completed>', re.DOTALL | re.IGNORECASE)
    final_answer_regex = re.compile(r'<final-answer>\s*(.*?)\s*</final-answer>', re.DOTALL | re.IGNORECASE)
    route_regex = re.compile(r'<route>\s*(.*?)\s*</route>', re.DOTALL | re.IGNORECASE)

    # Helper function to clean up task lists by removing bullet points, dashes, and extra characters
    def clean_task_list(task_string: str) -> list:
        if not task_string:
            return []
        # Remove the bullet markers like '- [ ]', '- [x]', and any extra dashes or spaces
        cleaned_tasks = re.sub(r'[-–]\s*\[\s*[x ]\s*\]|[-–]\s*', '', task_string, flags=re.IGNORECASE)
        # Split the cleaned tasks into a list and strip unnecessary spaces
        return [task.strip() for task in cleaned_tasks.split('\n') if task.strip()]

    # Extract values
    match = current_plan_regex.search(clean_response)
    if match: result['Current Plan'] = match.group(1).strip()
    
    match = pending_regex.search(clean_response)
    if match: result['Pending'] = clean_task_list(match.group(1).strip())
    
    match = completed_regex.search(clean_response)
    if match: result['Completed'] = clean_task_list(match.group(1).strip())
    
    match = final_answer_regex.search(clean_response)
    if match: result['Final Answer'] = match.group(1).strip()
    
    match = route_regex.search(clean_response)
    if match: result['Route'] = match.group(1).strip()
    
    # Infer route if not explicitly present
    if not result['Route']:
        if result['Final Answer']:
            result['Route'] = 'Final'
        elif result['Pending']:
            result['Route'] = 'Update'
            
    return result

    # Extract Current Plan
    current_plan_match = current_plan_regex.search(xml_response)
    if current_plan_match:
        current_plan_content = current_plan_match.group(1).strip()
        # Remove numeric prefixes like "1.", "2.", etc.
        result['Current Plan'] = [re.sub(r'^\d+\.\s*', '', task).strip() for task in current_plan_content.split('\n') if task.strip()]

    # Extract Pending tasks
    pending_match = pending_regex.search(xml_response)
    if pending_match:
        pending_content = pending_match.group(1).strip()
        result['Pending'] = clean_task_list(pending_content)

    # Extract Completed tasks
    completed_match = completed_regex.search(xml_response)
    if completed_match:
        completed_content = completed_match.group(1).strip()
        result['Completed'] = clean_task_list(completed_content)

    # Extract Final Answer
    final_answer_match = final_answer_regex.search(xml_response)
    if final_answer_match:
        result['Final Answer'] = final_answer_match.group(1).strip()

    # Extract Route
    route_match = route_regex.search(xml_response)
    if route_match:
        result['Route'] = route_match.group(1).strip()

    return result

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r',encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content