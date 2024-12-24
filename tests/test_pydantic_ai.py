from src.pydantic_ai import Agent, AgentResponse

def test_agent_initialization():
    """Test that agent initializes with default values"""
    agent = Agent(model="test-model")
    assert agent.model == "test-model"
    assert agent.temperature == 0.7
    assert len(agent.tools) == 2
    assert "introspect_schema" in agent.tools
    assert "execute_query" in agent.tools

def test_agent_tool_execution():
    """Test that agent can execute tools"""
    agent = Agent(model="test-model")
    result = agent.call_tool("execute_query", "SELECT * FROM test")
    assert isinstance(result, dict)
    assert "status" in result

def test_agent_run_sync():
    """Test synchronous prompt execution"""
    agent = Agent(model="test-model")
    response = agent.run_sync("Show me all users")
    assert isinstance(response, AgentResponse)
    assert isinstance(response.data, str)

def test_schema_context_check():
    """Test that agent requires schema context for queries"""
    agent = Agent(model="test-model")
    response = agent.run_sync("SELECT * FROM users")
    assert "introspect the schema first" in response.data.lower()
