import langchain_community.chains as c
print("chains module:", c.__file__)

# Try to find create_sql_query_chain
try:
    from langchain_community.chains.sql_database.query import create_sql_query_chain
    print("IMPORT OK: langchain_community.chains.sql_database.query")
except ImportError as e:
    print("FAIL1:", e)

try:
    from langchain_community.chains import create_sql_query_chain
    print("IMPORT OK: langchain_community.chains")
except ImportError as e:
    print("FAIL2:", e)

# Search manually
import os, langchain_community
base = os.path.dirname(langchain_community.__file__)
for root, dirs, files in os.walk(base):
    for f in files:
        if "sql" in f.lower() and "chain" in root.lower():
            print("FILE:", os.path.join(root, f))
