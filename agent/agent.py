# agent/agent.py

import json
from anthropic import Anthropic
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS
from .tool_executor import execute_tool

class LabMatcherAgent:
    def __init__(self, tool_callback=None, verbose=False):
        """
        Initialize the Lab Matcher Agent.

        Args:
            tool_callback: Optional callback function for tool execution events.
                          Called with (event_type, data) where event_type is
                          'tool_start' or 'tool_complete' and data contains tool info.
            verbose: If True and no callback provided, print tool execution to stdout.
        """
        self.client = Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.messages = []
        self.tool_callback = tool_callback
        self.verbose = verbose

    def run(self, user_input: str) -> str:
        """Process user input and return agent's response."""

        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        # Agent loop - keep going until we get a final response
        while True:
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.messages
            )

            # Check why the model stopped
            if response.stop_reason == "tool_use":
                # Model wants to use tools - execute them and continue
                self._handle_tool_use(response)
            else:
                # Model is done - extract and return the text response
                return self._handle_final_response(response)

    def _handle_tool_use(self, response):
        """Execute tool calls and add results to message history."""

        # Add assistant's response (which includes tool calls) to history
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Process each tool use block
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                # Notify callback or print (before execution)
                if self.tool_callback:
                    self.tool_callback('tool_start', {
                        'name': block.name,
                        'input': block.input,
                        'tool_use_id': block.id
                    })
                elif self.verbose:
                    # Backward compatibility: print if no callback but verbose=True
                    print(f"  → Calling tool: {block.name}")
                    print(f"    Input: {json.dumps(block.input, indent=2)}")

                # Execute the tool
                result = execute_tool(block.name, block.input)

                # Notify callback or print (after execution)
                if self.tool_callback:
                    self.tool_callback('tool_complete', {
                        'name': block.name,
                        'result': result,
                        'tool_use_id': block.id
                    })
                elif self.verbose:
                    # Backward compatibility: print if no callback but verbose=True
                    print(f"    Result: {result[:200]}..." if len(result) > 200 else f"    Result: {result}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Add tool results to history
        self.messages.append({
            "role": "user",
            "content": tool_results
        })

    def _handle_final_response(self, response) -> str:
        """Extract text from final response and update history."""
        
        # Add assistant's response to history
        self.messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Extract text blocks
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        return "\n".join(text_parts)

    def reset(self):
        """Clear conversation history."""
        self.messages = []
