import re

def extract_llm_response(xml_output):
    # Dictionary to store extracted data
    response_data = {
        "Route": None,
        "Thought": None,
        "Observation": None,
        "Final Answer": None,
        "Reflection": None
    }
    
    # Clean response from code blocks if present
    clean_output = re.sub(r'```[a-zA-Z]*\n?', '', xml_output)
    clean_output = re.sub(r'```', '', clean_output)

    # Define regex patterns for each field - more flexible and case-insensitive
    route_pattern = re.compile(r'<Route>(.*?)</Route>', re.DOTALL | re.IGNORECASE)
    thought_pattern = re.compile(r'<Thought>(.*?)</Thought>', re.DOTALL | re.IGNORECASE)
    observation_pattern = re.compile(r'<Observation>(.*?)</Observation>', re.DOTALL | re.IGNORECASE)
    final_answer_pattern = re.compile(r'<Final-Answer>(.*?)</Final-Answer>', re.DOTALL | re.IGNORECASE)
    reflection_pattern = re.compile(r'<Reflection>(.*?)</Reflection>', re.DOTALL | re.IGNORECASE)

    # Extract values based on the patterns
    route_match = route_pattern.search(clean_output)
    thought_match = thought_pattern.search(clean_output)
    observation_match = observation_pattern.search(clean_output)
    final_answer_match = final_answer_pattern.search(clean_output)
    reflection_match = reflection_pattern.search(clean_output)

    # Populate the dictionary if values are found
    if route_match:
        response_data['Route'] = route_match.group(1).strip()
        route_val = response_data['Route'].lower()

        # Based on Route, extract the rest of the data
        if route_val == "reason":
            if thought_match:
                response_data['Thought'] = thought_match.group(1).strip()
            if observation_match:
                response_data['Observation'] = observation_match.group(1).strip()

        elif route_val == "answer":
            if thought_match:
                response_data['Thought'] = thought_match.group(1).strip()
            if final_answer_match:
                response_data['Final Answer'] = final_answer_match.group(1).strip()

        elif route_val == "reflection":
            if thought_match:
                response_data['Thought'] = thought_match.group(1).strip()
            if reflection_match:
                response_data['Reflection'] = reflection_match.group(1).strip()
    
    # Fallback if Route is missing but we have Final Answer or Observation
    if not response_data['Route']:
        if final_answer_match:
            response_data['Route'] = 'Answer'
            response_data['Final Answer'] = final_answer_match.group(1).strip()
            if thought_match:
                response_data['Thought'] = thought_match.group(1).strip()
        elif observation_match:
            response_data['Route'] = 'Reason'
            response_data['Observation'] = observation_match.group(1).strip()
            if thought_match:
                response_data['Thought'] = thought_match.group(1).strip()
                
    return response_data

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r',encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content