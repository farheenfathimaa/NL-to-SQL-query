import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# Database connection
postgres_uri = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/query_db")
db = SQLDatabase.from_uri(postgres_uri)

def get_sql_chain():
    """Returns a chain that generates SQL from natural language."""
    return create_sql_query_chain(llm, db)

def get_explanation_chain():
    """Returns a chain that explains the SQL result in plain English."""
    template = """
    Given the following user question, corresponding SQL query, and SQL result, answer the user question in plain English.
    
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    return (
        RunnablePassthrough.assign(query=lambda x: x["query"], result=lambda x: x["result"])
        | prompt
        | llm
        | StrOutputParser()
    )

def run_query(question: str):
    """Generates SQL, executes it, and returns the result and explanation."""
    sql_chain = get_sql_chain()
    
    # Generate SQL
    generated_query = sql_chain.invoke({"question": question})
    
    # Clean query (remove markdown markers if any)
    query = generated_query.strip().replace("```sql", "").replace("```", "").strip()
    
    try:
        # Execute SQL
        result = db.run(query)
        
        # Explain Result
        explanation_chain = get_explanation_chain()
        explanation = explanation_chain.invoke({
            "question": question,
            "query": query,
            "result": result
        })
        
        return {
            "query": query,
            "result": result,
            "explanation": explanation,
            "status": "success"
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "status": "error"
        }
