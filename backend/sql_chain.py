import os
import re
import time as _time
from langchain_community.utilities import SQLDatabase
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---------------------------------------------------------------------------
# LLM provider configuration
# Primary: Groq (free, very generous limits — 30 RPM, 6000 req/day on free tier)
# Fallback: Google Gemini (if Groq key missing or also rate-limited)
# ---------------------------------------------------------------------------

_db = None
_llm_cache: dict = {}

# (provider, model_name) pairs tried in order
LLM_OPTIONS = [
    ("groq",   "llama-3.3-70b-versatile"),   # Best: fast, smart, generous free tier
    ("groq",   "llama3-8b-8192"),             # Groq fallback: smaller but still free
    ("groq",   "mixtral-8x7b-32768"),         # Groq fallback: Mixtral
    ("gemini", "gemini-1.5-flash"),           # Gemini fallback
    ("gemini", "gemini-1.5-flash-8b"),        # Gemini fallback
]

_current_option_index = 0


def get_db() -> SQLDatabase:
    """Returns a cached SQLDatabase connection (lazy init)."""
    global _db
    if _db is None:
        postgres_uri = os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@db:5432/query_db"
        )
        _db = SQLDatabase.from_uri(postgres_uri)
    return _db


def _build_llm(provider: str, model: str):
    """Instantiate an LLM for the given provider and model."""
    if provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in environment.")
        return ChatGroq(model=model, groq_api_key=api_key, temperature=0)

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in environment.")
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0)

    raise ValueError(f"Unknown provider: {provider}")


def get_llm(provider: str, model: str):
    """Returns a cached LLM instance for the given provider+model pair."""
    key = f"{provider}:{model}"
    if key not in _llm_cache:
        _llm_cache[key] = _build_llm(provider, model)
        print(f"[LLM] Initialized {provider} / {model}")
    return _llm_cache[key]


def _is_rate_limit_error(err: str) -> bool:
    return (
        "429" in err
        or "RESOURCE_EXHAUSTED" in err
        or "rate_limit_exceeded" in err
        or "rate limit" in err.lower()
        or "RateLimitError" in err
    )


def _is_daily_quota_exhausted(err: str) -> bool:
    """True when there's no point retrying the same model today."""
    return (
        "limit: 0" in err
        or "per_day" in err.lower()
        or "PerDay" in err
        or "tokens_per_day" in err.lower()
        or "requests_per_day" in err.lower()
    )


def _invoke_with_fallback(runnable_factory, inputs, max_retries: int = 3):
    """
    Try each LLM option in order. For per-minute rate limits: retry with
    backoff. For daily quota exhaustion: immediately move to the next option.
    """
    global _current_option_index

    for opt_idx in range(_current_option_index, len(LLM_OPTIONS)):
        provider, model = LLM_OPTIONS[opt_idx]
        try:
            runnable = runnable_factory(provider, model)
        except RuntimeError as e:
            # API key missing for this provider — skip entirely
            print(f"[LLM] Skipping {provider}/{model}: {e}")
            continue

        for attempt in range(max_retries):
            try:
                result = runnable.invoke(inputs)
                _current_option_index = opt_idx  # remember what worked
                return result
            except Exception as e:
                err = str(e)
                if _is_rate_limit_error(err):
                    if _is_daily_quota_exhausted(err):
                        print(f"[LLM] {provider}/{model} daily quota exhausted — switching model...")
                        break  # next option
                    # Per-minute limit — wait and retry
                    delay = 2.0 * (2 ** attempt)
                    m = re.search(r"[Rr]etry[^\d]*([0-9.]+)s", err)
                    if m:
                        delay = max(float(m.group(1)) + 1, delay)
                    print(f"[LLM] {provider}/{model} rate limited. Retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})")
                    _time.sleep(delay)
                else:
                    raise  # non-rate-limit error — surface it

        print(f"[LLM] {provider}/{model} exhausted. Trying next option...")

    tried = [f"{p}/{m}" for p, m in LLM_OPTIONS[_current_option_index:]]
    raise RuntimeError(
        f"All LLM options are quota-exhausted. Tried: {tried}. "
        "For Groq: quota resets every minute/day. "
        "For Gemini: quota resets daily. Please try again shortly."
    )


def run_query(question: str):
    """Generates SQL via LLM, executes it, and returns the result with explanation."""
    db = get_db()

    # --- Step 1: Generate SQL ---
    def make_sql_chain(provider, model):
        return create_sql_query_chain(get_llm(provider, model), db)

    generated_query = _invoke_with_fallback(make_sql_chain, {"question": question})
    print(f"[DEBUG] Raw SQL generation from Groq:\n{generated_query}\n---", flush=True)

    # Robust SQL extraction: handle preamble, markdown, and extra text
    query = generated_query
    if "SQLQuery:" in query:
        query = query.split("SQLQuery:")[-1]
        
    query = query.replace("```sql", "").replace("```", "").strip()
    
    # Find the SELECT statement and stop at the first semicolon (to prevent trailing garbage)
    match = re.search(r'(?i)(SELECT\b.+?(?:;|$))', query, flags=re.DOTALL)
    if match:
        query = match.group(1).strip()
    else:
        query = query.strip()
        
    print(f"[DEBUG] Extracted SQL:\n{query}\n---", flush=True)

    try:
        # --- Step 2: Execute SQL ---
        result = db.run(query)

        # --- Step 3: Explain result in plain English ---
        prompt = ChatPromptTemplate.from_template("""
Given the following user question, corresponding SQL query, and SQL result,
answer the user question in plain English.

Question: {question}
SQL Query: {query}
SQL Result: {result}

Answer:""")

        def make_explanation_chain(provider, model):
            return (
                RunnablePassthrough.assign(
                    query=lambda x: x["query"],
                    result=lambda x: x["result"],
                )
                | prompt
                | get_llm(provider, model)
                | StrOutputParser()
            )

        explanation = _invoke_with_fallback(
            make_explanation_chain,
            {"question": question, "query": query, "result": result},
        )

        return {
            "query": query,
            "result": result,
            "explanation": explanation,
            "status": "success",
        }

    except RuntimeError:
        raise  # surface quota errors to the API layer
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "status": "error",
        }
