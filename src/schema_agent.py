from google import generativeai as genai
from pydantic import BaseModel
from src.introspect import introspect_database
from src.query_tools import QueryTools
import json

def debug_log(func_name: str, *args, **kwargs):
    """Debug logging helper"""
    print("\n" + "="*80)
    print(f"🔧 TOOL CALLED: {func_name}")
    print(f"📥 INPUTS:")
    for i, arg in enumerate(args):
        print(f"  Arg {i}: {str(arg)[:200]}{'...' if len(str(arg)) > 200 else ''}")
    for k, v in kwargs.items():
        print(f"  {k}: {str(v)[:200]}{'...' if len(str(v)) > 200 else ''}")
    print("-"*80)

def log_result(result):
    """Log tool results"""
    print(f"📤 OUTPUT:")
    print(f"  {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
    print("="*80 + "\n")

class Agent:
    def __init__(self, model_name: str, deps_type: type, system_prompt: str):
        self.model = genai.GenerativeModel(model_name)
        self.deps_type = deps_type
        self.system_prompt = system_prompt
        self._tools = {}  # Store decorated tools
        self.query_tools = None
        self.current_schema = None
        
    def tool_plain(self, func):
        def wrapper(*args, **kwargs):
            debug_log(func.__name__, *args, **kwargs)
            result = func(*args, **kwargs)
            log_result(result)
            return result
        setattr(self, func.__name__, wrapper)
        return wrapper
        
    def tool(self, func):
        def wrapper(*args, **kwargs):
            debug_log(func.__name__, *args, **kwargs)
            result = func(*args, **kwargs)
            log_result(result)
            return result
        setattr(self, func.__name__, wrapper)
        return wrapper
        
    def run_sync(self, prompt: str, deps: str = None):
        print("\n" + "="*80)
        print("🤖 AI MODEL CALLED")
        print(f"📝 PROMPT:")
        print(f"{prompt[:500]}{'...' if len(prompt) > 500 else ''}")
        print("-"*80)
        response = self.model.generate_content(prompt)
        print(f"💭 RESPONSE:")
        print(f"{str(response.text)[:500]}{'...' if len(str(response.text)) > 500 else ''}")
        print("="*80 + "\n")
        return response

agent = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    system_prompt=(
        "You're a database schema expert. You help users understand database schemas "
        "by analyzing the structure and relationships between tables. "
        "Use clear, technical language to explain schema details when asked."
    ),
)

@agent.tool
def build_sql_query(schema_json: str, question: str) -> str:
    """Convert natural language question to SQL query"""
    try:
        prompt = f"""
        Given this database schema and question, create a SQL query to answer it.
        Important guidelines:
        - Only return the SQL query, nothing else
        - Use ILIKE instead of LIKE for case-insensitive string matching
        - When searching for names or text, always use case-insensitive comparison
        
        Schema:
        {schema_json}
        
        Question: {question}
        """
        response = agent.run_sync(prompt)
        return str(response.text).strip()
    except Exception as e:
        return f"Error building query: {str(e)}"

@agent.tool
def execute_sql_query(connection_string: str, query: str) -> str:
    """Execute SQL query and return results"""
    if agent.query_tools is None:
        agent.query_tools = QueryTools(connection_string)
        if agent.current_schema:
            agent.query_tools.update_schema_info(agent.current_schema)

    success, message, results = agent.query_tools.execute_query(query)
    if not success:
        return f"Query execution failed: {message}"

    return results.to_string() if results is not None else "No results"

@agent.tool_plain
def get_schema(connection_string: str, schema_name: str = 'public') -> str:
    """Introspect database schema"""
    try:
        result = introspect_database(connection_string, schema_name)
        agent.current_schema = result  # Store for query tools
        if agent.query_tools:
            agent.query_tools.update_schema_info(result)
        return result
    except Exception as e:
        return json.dumps({"error": f"Failed to introspect schema: {str(e)}"})

@agent.tool
def analyze_query_results(results: str, analysis_question: str) -> str:
    """Analyze query results and provide insights"""
    try:
        prompt = f"""
        Analyze these query results and answer the following question:
        {analysis_question}

        Query Results:
        {results}

        Provide a clear, concise analysis focusing specifically on the question asked.
        """
        response = agent.run_sync(prompt)
        return str(response.text).strip()
    except Exception as e:
        return f"Error analyzing results: {str(e)}"

@agent.tool
def suggest_visualization(results: str, visualization_question: str) -> str:
    """Suggest appropriate visualization for query results"""
    try:
        prompt = f"""
        Given these query results:
        {results}

        And this visualization question:
        {visualization_question}

        Suggest the most appropriate way to visualize this data. Include:
        1. The type of chart/visualization
        2. Why this visualization would be effective
        3. Key aspects to highlight in the visualization

        Keep the response concise and focused on visualization recommendations.
        """
        response = agent.run_sync(prompt)
        return str(response.text).strip()
    except Exception as e:
        return f"Error suggesting visualization: {str(e)}"

@agent.tool
def analyze_schema(schema_json: str, question: str) -> str:
    """
    Analyze a schema and provide insights about its structure based on a specific question.
    
    Args:
        schema_json: JSON string containing schema information
        question: Specific question about the schema to answer
    Returns:
        Analysis answering the specific question about the schema
    """
    try:
        schema = json.loads(schema_json)
        if "error" in schema:
            return f"Error analyzing schema: {schema['error']}"
            
        # Use the question to guide the analysis
        response = agent.run_sync(f"""
        Analyze this database schema and answer the following question: {question}
        
        Schema details:
        {json.dumps(schema, indent=2)}
        """)
        
        return str(response.text)
    except Exception as e:
        return f"Error analyzing schema: {str(e)}"
