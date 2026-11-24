"""RoleFit Agent — a conversational LLM job-matching agent.

A person states what they want (and what they'd never take) in plain
words, over a conversation. An LLM agent with tool use and structured
outputs understands it, remembers context across turns, retrieves
matching roles from a jobs index, ranks them with a plain-words reason
for each, and refines as the person replies.
"""

__version__ = "0.1.0"
