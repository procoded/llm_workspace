from src.schema_agent import agent
import json

def main():
    print("\n🚀 Starting Schema Agent Test\n")
    
    # Test connection string - replace with your actual database connection
    connection_string = "postgresql://postgres:postgres@localhost:5432/nestjs"
    
    print("📊 Getting schema...")
    try:
        # First get the schema
        schema_json = agent.get_schema(connection_string)
        print("\n✅ Schema retrieved successfully!")
        
        # Add data analysis questions
        questions = [
            {
                "question": "how many properties are on street princeton?",
                "analysis": "What patterns do you see in the results?",
                "visualization": "What's the best way to visualize this data?"
            },
            {
                "question": "show me the average property value by county",
                "analysis": "Which counties have the highest values?",
                "visualization": "Suggest a chart type for this data"
            }
        ]
        
        print("\n🔍 Starting Analysis...")
        
        for q in questions:
            print("\n" + "="*80)
            print(f"❓ Question: {q['question']}")
            print("="*80)
            
            # Build SQL query
            sql_query = agent.build_sql_query(schema_json, q['question'])
            
            # Execute query
            results = agent.execute_sql_query(connection_string, sql_query)
            
            # Analyze results
            analysis = agent.analyze_query_results(results, q['analysis'])
            
            # Get visualization suggestion
            viz = agent.suggest_visualization(results, q['visualization'])
            
            print("\n📊 Results Summary:")
            print("-"*40)
            print(f"Query Results: {results}")
            print(f"Analysis: {analysis}")
            print(f"Visualization: {viz}")
            print("="*80)
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
