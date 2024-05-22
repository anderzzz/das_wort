"""Vinnova grant analysis

Written by: Anders Ohrn, 2024 May

"""
import os
import json
from typing import List, Dict, Optional, Union

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from mistralai.client import MistralClient

from vinnova_drl import VinnovaDataRetrievalLayer


class MessageStack:
    def __init__(self):
        self._message_collection = []

    def __repr__(self):
        ret_str = ''
        for row in self._message_collection:
            if isinstance(row, Dict):
                ret_str += f'{row["role"]}: {row["content"]}\n'
            elif isinstance(row, ChatCompletionMessage):
                ret_str += f'assistant: {row.content}\n'
            ret_str += '=' * 50
            ret_str += '\n'
        return ret_str[:-51]

    def _add_payload(self, payload: Union[Dict[str, str], ChatCompletionMessage]):
        self._message_collection.append(payload)

    def set_system_instruction(self, value: str):
        for row in self._message_collection:
            if isinstance(row, Dict):
                if row['role'] == 'system':
                    row['content'] = value
                    break
        else:
            self._add_payload({'role': 'system', 'content': value})

    def add_user_message(self, content: str):
        payload = {'role': 'user', 'content': content}
        self._add_payload(payload)

    def add_assistant_message(self, content: ChatCompletionMessage):
        self._add_payload(content)

    def add_tool_message(self, content: str, tool_call_id: str, name: str, type: str):
        payload = {'role': 'tool', 'content': content, 'tool_call_id': tool_call_id, 'name': name, 'type': type}
        self._add_payload(payload)

    def get_message_stack(self):
        return self._message_collection

    def delete(self, slc):
        del self._message_collection[slc]


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def send_request_to_openai_chat_completion(
        client: OpenAI,
        messages: List[Dict[str, str]],
        model: str = 'gpt-4-turbo-2024-04-09',
        tools: Optional[List[str]] = None,
        tool_choice: str = 'auto',
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        n_completions: int = 1,
):
    kwargs = {
        'model': model,
        'messages': messages,
        'tools': tools,
        'tool_choice': tool_choice,
        'temperature': temperature,
        'top_p': top_p,
        'max_tokens': max_tokens,
        'frequency_penalty': frequency_penalty,
        'presence_penalty': presence_penalty,
        'n': n_completions
    }
    if tools is None:
        del kwargs['tools']
        del kwargs['tool_choice']

    try:
        openai_completion = client.chat.completions.create(**kwargs)
    except Exception as e:
        raise e

    return openai_completion


class SemanticEngine:
    """Bla bla

    """
    def __init__(self,
                 client: Union[OpenAI, MistralClient],
                 system_definition: str,
                 llm_params: Dict,
                 tools: Optional[List[VinnovaDataRetrievalLayer]] = None,
                 respond_to_function: bool = True
                 ):
        self.client = client
        self.message_stack = MessageStack()
        self.message_stack.set_system_instruction(system_definition)
        self.llm_params = llm_params
        self.respond_to_function = respond_to_function

        self.tools_str = None
        if tools is not None:
            self.tools_str = []
            for tool in tools:
                self.tools_str.append(tool.specification_str)
        self.tools = tools

    def process(self, user_message: str):
        self.message_stack.add_user_message(user_message)
        response = send_request_to_openai_chat_completion(
            client=self.client,
            messages=self.message_stack.get_message_stack(),
            tools=self.tools_str,
            **self.llm_params
        )
        response_message = response.choices[0].message
        self.message_stack.add_assistant_message(response_message)

        if response_message.tool_calls is not None:
            for tool_call in response_message.tool_calls:
                tool_call_id = tool_call.id
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                tool = next(filter(lambda x: x.name == function_name, self.tools))
                tool_response = tool(**function_args)

                self.message_stack.add_tool_message(
                    content=json.dumps(tool_response),
                    tool_call_id=tool_call_id,
                    name=function_name,
                    type='function'
                )

            if self.respond_to_function:
                response = send_request_to_openai_chat_completion(
                    client=self.client,
                    messages=self.message_stack.get_message_stack(),
                    tools=self.tools_str,
                    **self.llm_params
                )
                self.message_stack.add_assistant_message(response.choices[0].message)

