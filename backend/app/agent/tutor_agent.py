import json
from typing import List, Dict, Any
import httpx
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings

class TutorAgent:
    def __init__(self, tutor_data: Dict[str, Any]):
        self.tutor_data = tutor_data
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True,
            handle_parsing_errors=True
        )

    def _create_tools(self):
        knowledge_url = self.tutor_data.get("knowledge_source")
        
        @tool
        def fetch_knowledge(query: str) -> str:
            """Fetch relevant knowledge from the tutor's knowledge source."""
            if not knowledge_url:
                return "No knowledge source configured for this tutor."
            
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(knowledge_url)
                    if response.status_code == 200:
                        content = response.text[:5000]  # Limit for demo
                        return f"Knowledge from source:\n{content}"
                    return f"Could not access knowledge source (status: {response.status_code})"
            except Exception as e:
                return f"Error accessing knowledge: {str(e)}"
        
        return [fetch_knowledge]

    def _create_agent(self):
        system_prompt = f"""You are a helpful tutor assistant.
        
        Tutor Name: {self.tutor_data.get('name', 'Tutor')}
        Tutor Description: {self.tutor_data.get('description', 'No description')}
        
        Instructions:
        {self.tutor_data.get('instructions', 'Be helpful and friendly.')}
        
        You have access to tools to fetch knowledge from the tutor's knowledge source.
        Use the fetch_knowledge tool when you need information from the knowledge base.
        
        If you don't know something, say so honestly.
        Be conversational and engaging.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return create_tool_calling_agent(self.llm, self.tools, prompt)

    async def chat(self, message: str, history: List[Dict[str, str]] = None) -> str:
        """Process a chat message and return the response."""
        try:
            # Convert history to LangChain format
            chat_history = []
            if history:
                for msg in history:
                    chat_history.append(("human" if msg["role"] == "user" else "ai", msg["content"]))
            
            response = await self.executor.ainvoke({
                "input": message,
                "chat_history": chat_history
            })
            return response["output"]
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}"

# Simple factory
def get_tutor_agent(tutor_data: dict):
    return TutorAgent(tutor_data)
