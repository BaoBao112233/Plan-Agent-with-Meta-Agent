import xml.etree.ElementTree as ET
import re

def extract_from_xml(xml_string):
    # Try to find the <Agent> block in case LLM added extra text
    match = re.search(r'<Agent>.*?</Agent>', xml_string, re.DOTALL | re.IGNORECASE)
    if match:
        xml_to_parse = match.group(0)
    else:
        # Fallback to the whole string if no <Agent> tag found, maybe it's implicitly there or malformed
        xml_to_parse = xml_string

    # Parse the XML string
    try:
        # Basic cleanup: remove markdown code block delimiters if they wrap the XML
        xml_to_parse = re.sub(r'```[a-zA-Z]*\n?', '', xml_to_parse)
        xml_to_parse = re.sub(r'```', '', xml_to_parse)
        root = ET.fromstring(xml_to_parse)
    except ET.ParseError as e:
        # If ET fails, try a regex fallback for key fields
        result = {
            'Agent Name': None,
            'Agent Description': None,
            'Agent Query': None,
            'Tasks': [],
            'Tool': None,
            'Answer': None
        }
        name_match = re.search(r'<Agent-Name>(.*?)</Agent-Name>', xml_string, re.DOTALL | re.IGNORECASE)
        desc_match = re.search(r'<Agent-Description>(.*?)</Agent-Description>', xml_string, re.DOTALL | re.IGNORECASE)
        query_match = re.search(r'<Agent-Query>(.*?)</Agent-Query>', xml_string, re.DOTALL | re.IGNORECASE)
        answer_match = re.search(r'<Answer>(.*?)</Answer>', xml_string, re.DOTALL | re.IGNORECASE)
        
        if name_match: result['Agent Name'] = name_match.group(1).strip()
        if desc_match: result['Agent Description'] = desc_match.group(1).strip()
        if query_match: result['Agent Query'] = query_match.group(1).strip()
        if answer_match: result['Answer'] = answer_match.group(1).strip()
        
        tasks_match = re.search(r'<Tasks>(.*?)</Tasks>', xml_string, re.DOTALL | re.IGNORECASE)
        if tasks_match:
            tasks_content = tasks_match.group(1).strip()
            # If tasks is already a list-like string, we might need more parsing
            # For now, let's try to find individual <task> items if they exist
            task_items = re.findall(r'<Task>(.*?)</Task>', tasks_content, re.IGNORECASE)
            if task_items:
                result['Tasks'] = [t.strip() for t in task_items]
            else:
                # Fallback: split by lines or commas
                result['Tasks'] = [t.strip() for t in tasks_content.split('\n') if t.strip()]
        
        return result
    
    # Initialize the result dictionary
    result = {
        'Agent Name': None,
        'Agent Description': None,
        'Agent Query': None,
        'Tasks': [],
        'Tool': None,
        'Answer': None
    }
    
    # Check if root tag is "Agent"
    if root.tag == "Agent":
        # Extract Agent Name
        agent_name = root.find("./Agent-Name")
        if agent_name is not None:
            result['Agent Name'] = agent_name.text.strip()
        
        # Extract Agent Description
        agent_description = root.find("./Agent-Description")
        if agent_description is not None:
            result['Agent Description'] = agent_description.text.strip()
        
        # Extract Agent Query
        agent_query = root.find("./Agent-Query")
        if agent_query is not None:
            result['Agent Query'] = agent_query.text.strip()
        
        # Extract Tasks
        tasks = root.findall("./Tasks/Task")
        for task in tasks:
            if task is not None and task.text:
                result['Tasks'].append(task.text.strip())
        
        # Extract Tool (if present)
        tool = root.find("./Tool")
        if tool is not None:
            tool_info = {}
            tool_name = tool.find("Tool-Name")
            tool_description = tool.find("Tool-Description")
            if tool_name is not None:
                tool_info['Tool Name'] = tool_name.text.strip()
            if tool_description is not None:
                tool_info['Tool Description'] = tool_description.text.strip()
            result['Tool'] = tool_info
    
    # Check if root tag is "Final-Answer"
    elif root.tag == "Final-Answer":
        result['Answer'] = root.text.strip()
    return result

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r',encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content