import os
from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.schema import AIMessage, HumanMessage, SystemMessage


DEPENDENCY_FILES = [
    "package.json",
    "requirements.txt",
    "Pipfile",
    "pyproject.toml",
    "poetry.lock",
    "package-lock.json",
    "yarn.lock",
    "composer.json",
    "Gemfile",
    "Gemfile.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock"
]

openai_api_key = os.getenv("OPENAI_API_KEY")

def read_changed_code_files(filenames: List[str]) -> str:
    content = ""
    for fname in filenames:
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                file_content = f.read()
            content += f"### {fname}\n{file_content}\n\n"
    return content or "No code files found."

def read_dependency_files() -> str:
    content = ""
    for file in DEPENDENCY_FILES:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                file_content = f.read()
            content += f"### {file}\n{file_content}\n\n"
    return content or "No dependency files found."

def code_review_tool_func(code_content: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, openai_api_key=openai_api_key)
    messages = [
        SystemMessage(content="You are an expert AI code reviewer. Review the following code for quality, potential issues, and improvements. Limit to 300 words."),
        HumanMessage(content=code_content),
    ]
    response = llm(messages)
    return response.content

code_review_tool = Tool(
    name="Code Review",
    func=code_review_tool_func,
    description="Review code files for quality, bugs, and improvements."
)

def security_scan_deps_tool_func(deps_content: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
    messages = [
        SystemMessage(content="You are a security expert reviewing software dependencies for vulnerabilities and risks. Provide concise feedback."),
        HumanMessage(content=deps_content),
    ]
    response = llm(messages)
    return response.content

security_scan_tool = Tool(
    name="Dependency Security Scan",
    func=security_scan_deps_tool_func,
    description="Analyze dependency files for security vulnerabilities and outdated packages."
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)

agent = initialize_agent(
    tools=[code_review_tool, security_scan_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=False,
)

if __name__ == "__main__":
    changed_files_str = os.getenv("CHANGED_FILES", "")
    changed_files = changed_files_str.split(",") if changed_files_str else []

    code_content = read_changed_code_files(changed_files)
    deps_content = read_dependency_files()

    prompt = f"""You have two tasks:
    1) Code Review: Review this changed code for bugs, quality, and improvements:
    {code_content}

    2) Security Scan: Review these dependencies for vulnerabilities:
    {deps_content}

    Please use the appropriate tool and provide separate, clear feedback for each task.
    """

    result = agent.run(prompt)
    print(result)
