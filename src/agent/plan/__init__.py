from src.agent.plan.utils import extract_plan,read_markdown_file,extract_llm_response
from src.message import AIMessage,HumanMessage,SystemMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from src.agent.plan.state import PlanState,UpdateState
from langgraph.graph import StateGraph,END,START
from IPython.display import display,Image
from src.inference import BaseInference
from src.agent.meta import MetaAgent
from src.router import LLMRouter
from src.agent import BaseAgent
from src.api_client import APIClient
from termcolor import colored
from datetime import datetime
import time

class PlanAgent(BaseAgent):
    def __init__(self,max_iteration=10,llm:BaseInference=None,verbose=False,api_enabled=True):
        self.name='Plan Agent'
        self.max_iteration=max_iteration
        self.graph=self.create_graph()
        self.verbose=verbose
        self.iteration=0
        self.llm=llm
        self.api_enabled=api_enabled
        self.api_client=APIClient() if api_enabled else None
        self.start_time=None
        self.current_input=None
    
    def router(self,state:PlanState):
        routes=[
            {
                'route': 'simple',
                'description': 'This route handles straightforward tasks with no user interaction. It generates a plan in one step, making it ideal for clear, uncomplicated problems that can be quickly solved.'
            },
            {
                'route': 'advanced',
                'description': 'This route is tailored for more complex, involved or ambiguous tasks that require additional information or user preferences. It involves multiple interactions to refine the plan based on specific needs, ensuring a more comprehensive and customized solution. This route is ideal for tasks that need deeper understanding or nuanced decision-making.'
            }
        ]
        query=state.get('input')
        router=LLMRouter(routes=routes,llm=self.llm,verbose=False)
        plan_type=router.invoke(query)
        return {**state,'plan_type':plan_type}

    def simple_plan(self,state:PlanState):
        system_prompt=read_markdown_file('./src/agent/plan/prompt/simple_plan.md')
        llm_response=self.llm.invoke([SystemMessage(system_prompt),HumanMessage(state.get('input'))])
        plan_data=extract_plan(llm_response.content)
        plan=plan_data.get('Plan')
        if self.verbose:
            print(colored(f'Plan:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(plan)])}',color='green',attrs=['bold']))
        
        # Gửi plan lên API
        if self.api_enabled and self.api_client:
            api_data = {
                "input": state.get('input'),
                "plan_type": "simple",
                "current_plan": plan,
                "pending_tasks": plan.copy(),
                "completed_tasks": [],
                "current_task": plan[0] if plan else "",
                "status": "plan_created",
                "timestamp": datetime.now().isoformat()
            }
            self.api_client.send_plan_status(api_data)
        
        return {**state,'plan':plan}
    
    def advance_plan(self,state:PlanState):
        system_prompt=read_markdown_file('./src/agent/plan/prompt/advanced_plan.md')
        messages=[SystemMessage(system_prompt),HumanMessage(state.get('input'))]
        llm_response=self.llm.invoke(messages)
        plan_data=extract_plan(llm_response.content)
        route=plan_data.get('Route')
        while route!='Plan':
            question=plan_data.get('Question')
            messages.pop(-1)
            answer=input(f'{question}\nUser: ')
            user_prompt=f'<option>\n<question>{question}</question>\n<answer>{answer}</answer>\n<route>{route}</route>\n</option>'
            messages.append(HumanMessage(user_prompt))
            llm_response=self.llm.invoke(messages)
            messages.append(AIMessage(llm_response.content))
            plan_data=extract_plan(llm_response.content)
            route=plan_data.get('Route')
        plan=plan_data.get('Plan')
        if self.verbose:
            print(colored(f'Plan:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(plan)])}',color='green',attrs=['bold']))
        
        # Gửi plan lên API
        if self.api_enabled and self.api_client:
            api_data = {
                "input": state.get('input'),
                "plan_type": "advanced",
                "current_plan": plan,
                "pending_tasks": plan.copy(),
                "completed_tasks": [],
                "current_task": plan[0] if plan else "",
                "status": "plan_created",
                "timestamp": datetime.now().isoformat()
            }
            self.api_client.send_plan_status(api_data)
        
        return {**state,'plan':plan}


    def initialize(self,state:UpdateState):
        system_prompt=read_markdown_file('./src/agent/plan/prompt/update.md')
        plan_list = state.get('plan', [])
        current = plan_list[0] if plan_list else ""
        pending = plan_list or []
        completed = []
        
        if self.verbose:
            if pending:
                print(colored(f'Pending Tasks:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(pending)])}',color='yellow',attrs=['bold']))
            if completed:
                print(colored(f'Completed Tasks:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(completed)])}',color='blue',attrs=['bold']))
        
        # Khởi tạo tất cả tasks với status "pending" trên API
        if self.api_enabled and self.api_client:
            for task in pending:
                self.api_client.update_task_status(task, "pending")
            
            # Update plan status to "in_progress" 
            self.api_client.update_plan_status("in_progress")
        
        messages=[SystemMessage(system_prompt)]
        return {**state,'messages':messages,'current':current,'pending':pending,'completed':completed,'output':''}
    
    def execute_task(self,state:UpdateState):
        plan=state.get('plan')
        current=state.get('current')
        responses=state.get('responses')
        
        # Update task status to "in_progress" trước khi execute
        if self.api_enabled and self.api_client:
            self.api_client.update_task_status(current, "in_progress")
        
        agent=MetaAgent(llm=self.llm,verbose=self.verbose)
        task_response=agent.invoke(f'Information:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(responses)])}\nTask:\n{current}')
        
        if self.verbose:
            print(colored(f'Current Task:\n{current}',color='cyan',attrs=['bold']))
            print(colored(f'Task Response:\n{task_response}',color='cyan',attrs=['bold']))
        
        # Update task với execution result
        if self.api_enabled and self.api_client:
            self.api_client.update_task_status(current, "completed", task_response)
        
        # Truncate task_response if too long to prevent payload issues
        max_response_length = 2000
        if len(task_response) > max_response_length:
            task_response_truncated = task_response[:max_response_length] + "... [response truncated for brevity]"
        else:
            task_response_truncated = task_response
            
        user_prompt=f'Plan:\n{plan}\nTask:\n{current}\nTask Response:\n{task_response_truncated}'
        messages=[HumanMessage(user_prompt)]
        return {**state,'messages':messages,'responses':[task_response]}

    def trim_messages(self, messages, max_tokens=4000):
        """Trim messages to prevent payload too large error"""
        if not messages:
            return messages
            
        # Keep only the most recent messages that fit within token limit
        trimmed = []
        total_chars = 0
        
        # Reverse to process from newest to oldest
        for msg in reversed(messages):
            msg_chars = len(str(msg.content))
            if total_chars + msg_chars > max_tokens * 4:  # Rough char to token ratio
                break
            trimmed.insert(0, msg)
            total_chars += msg_chars
            
        # Always keep at least the last message
        if not trimmed and messages:
            last_msg = messages[-1]
            # Truncate content if too long
            if len(str(last_msg.content)) > max_tokens * 4:
                content = str(last_msg.content)[:max_tokens * 4] + "... [truncated]"
                trimmed = [type(last_msg)(content)]
            else:
                trimmed = [last_msg]
                
        return trimmed

    def update_plan(self,state:UpdateState):
        # Trim messages to prevent payload too large
        messages = self.trim_messages(state.get('messages', []))
        llm_response=self.llm.invoke(messages)
        plan_data=extract_llm_response(llm_response.content)
        plan=plan_data.get('Plan')
        pending=plan_data.get('Pending') or []  # Default to empty list if None
        completed=plan_data.get('Completed') or []  # Default to empty list if None
        
        if self.verbose:
            if pending:
                print(colored(f'Pending Tasks:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(pending)])}',color='yellow',attrs=['bold']))
            if completed:
                print(colored(f'Completed Tasks:\n{'\n'.join([f'{index+1}. {task}' for index,task in enumerate(completed)])}',color='blue',attrs=['bold']))
        
        # Update task statuses trên API
        if self.api_enabled and self.api_client:
            # Lấy task trước đó để so sánh
            previous_completed = state.get('completed', [])
            previous_pending = state.get('pending', [])
            
            # Tìm tasks vừa được completed
            newly_completed = [task for task in completed if task not in previous_completed]
            for task in newly_completed:
                self.api_client.update_task_status(task, "completed", f"Task '{task}' hoàn thành thành công")
            
            # Update pending tasks status
            for task in pending:
                if task not in previous_pending:  # New pending task
                    self.api_client.update_task_status(task, "pending")
            
            # Update plan status
            if not pending:  # Tất cả tasks đã completed
                self.api_client.update_plan_status("completed")
            else:
                self.api_client.update_plan_status("in_progress")
        
        if pending:
            current=pending[0]
        else:
            current=''
        # Keep the completed list we already processed instead of overwriting with potentially None
        completed_final = plan_data.get('Completed') or []
        return {**state,'plan':plan,'current':current,'pending':pending,'completed':completed_final}
    
    def final(self,state:UpdateState):
        user_prompt='All Tasks completed successfully. Now give the final answer.'
        llm_response=self.llm.invoke(state.get('messages')+[HumanMessage(user_prompt)])
        plan_data=extract_llm_response(llm_response.content)
        output=plan_data.get('Final Answer')
        
        # Hoàn thành plan trên API
        if self.api_enabled and self.api_client:
            self.api_client.update_plan_status("completed", output)
            
            if self.verbose:
                print("🎉 Plan execution completed! All data sent to API.")
        
        return {**state,'output':output}

    def plan_controller(self,state:UpdateState):
        if state.get('pending'):
            return 'task'
        else:
            return 'final'

    def route_controller(self,state:PlanState):
        return state.get('plan_type')

    def create_graph(self):
        graph=StateGraph(PlanState)
        graph.add_node('route',self.router)
        graph.add_node('simple',self.simple_plan)
        graph.add_node('advanced',self.advance_plan)
        graph.add_node('execute',lambda _:self.update_graph())

        graph.add_edge(START,'route')
        graph.add_conditional_edges('route',self.route_controller)
        graph.add_edge('simple','execute')
        graph.add_edge('advanced','execute')
        graph.add_edge('execute',END)

        return graph.compile(debug=False)
    
    def update_graph(self):
        graph=StateGraph(UpdateState)
        graph.add_node('inital',self.initialize)
        graph.add_node('task',self.execute_task)
        graph.add_node('update',self.update_plan)
        graph.add_node('final',self.final)

        graph.add_edge(START,'inital')
        graph.add_edge('inital','task')
        graph.add_edge('task','update')
        graph.add_conditional_edges('update',self.plan_controller)
        graph.add_edge('final',END)

        return graph.compile(debug=False)

    def invoke(self,input:str):
        # Lưu thời gian bắt đầu và input để sử dụng cho API
        self.start_time = time.time()
        self.current_input = input
        
        if self.verbose:
            print(f'Entering '+colored(self.name,'black','on_white'))
        state={
            'input': input,
            'plan_status':'',
            'route':'',
            'plan': [],
            'output': ''
        }
        agent_response=self.graph.invoke(state)
        return agent_response['output']


    def stream(self, input: str):
        pass