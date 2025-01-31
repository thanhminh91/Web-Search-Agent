from src.message import AIMessage,BaseMessage,HumanMessage,ImageMessage,SystemMessage,ToolMessage
from requests import get,RequestException,HTTPError,ConnectionError
from tenacity import retry,stop_after_attempt,retry_if_exception_type
from ratelimit import limits,sleep_and_retry
from src.inference import BaseInference,Token
from httpx import Client,AsyncClient
from pydantic import BaseModel
from typing import Literal
from json import loads
from uuid import uuid4

class ChatOpenRouter(BaseInference):
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, messages: list[BaseMessage],json=False,model:BaseModel|None=None) -> AIMessage|ToolMessage|BaseModel:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://openrouter.ai/api/v1/chat/completions"
        contents=[]
        for message in messages:
            if isinstance(message,SystemMessage):
                if model:
                    message.content=self.structured(message,model) 
                contents.append(message.to_dict())
            if isinstance(message,(HumanMessage,AIMessage)):
                contents.append(message.to_dict())
            if isinstance(message,ImageMessage):
                text,image=message.content
                contents.append([
                    {
                        'role':'user',
                        'content':[
                            {
                                'type':'text',
                                'text':text
                            },
                            {
                                'type':'image_url',
                                'image_url':{
                                    'url':image
                                }
                            }
                        ]
                    }
                ])

        payload={
            "model": self.model,
            "messages": contents,
            "temperature": temperature,
            "response_format": {
                "type": "json_object" if json or model else "text"
            },
            "stream":False,
        }
        if self.tools:
            payload["tools"]=[{
                'type':'function',
                'function':{
                    'name':tool.name,
                    'description':tool.description,
                    'parameters':tool.schema
                }
            } for tool in self.tools]
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,timeout=None)
            json_object=response.json()
            # print(json_object)
            if json_object.get('error'):
                raise HTTPError(json_object['error']['message'])
            message=json_object['choices'][0]['message']
            usage_metadata=json_object['usage']
            input,output,total=usage_metadata['prompt_tokens'],usage_metadata['completion_tokens'],usage_metadata['total_tokens']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(message.get('content'))
            if json:
                return AIMessage(loads(message.get('content')))
            if message.get('content'):
                return AIMessage(message.get('content'))
            else:
                tool_call=message.get('tool_calls')[0]['function']
                return ToolMessage(id=str(uuid4()),name=tool_call['name'],args=tool_call['arguments']) 
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self, messages: list[BaseMessage],json=False,model:BaseModel=None) -> AIMessage|ToolMessage|BaseModel:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://api.groq.com/openai/v1/chat/completions"
        contents=[]
        for message in messages:
            if isinstance(message,SystemMessage):
                if model:
                    message.content=self.structured(message,model) 
                contents.append(message.to_dict())
            if isinstance(message,(HumanMessage,AIMessage)):
                contents.append(message.to_dict())
            if isinstance(message,ImageMessage):
                text,image=message.content
                contents.append([
                    {
                        'role':'user',
                        'content':[
                            {
                                'type':'text',
                                'text':text
                            },
                            {
                                'type':'image_url',
                                'image_url':{
                                    'url':image
                                }
                            }
                        ]
                    }
                ])

        payload={
            "model": self.model,
            "messages": contents,
            "temperature": temperature,
            "response_format": {
                "type": "json_object" if json or model else "text"
            },
            "stream":False,
        }
        if self.tools:
            payload["tools"]=[{
                'type':'function',
                'function':{
                    'name':tool.name,
                    'description':tool.description,
                    'parameters':tool.schema
                }
            } for tool in self.tools]
        try:
            async with AsyncClient() as client:
                response=await client.post(url=url,json=payload,headers=headers,timeout=None)
            json_object=response.json()
            # print(json_object)
            if json_object.get('error'):
                raise HTTPError(json_object['error']['message'])
            message=json_object['choices'][0]['message']
            usage_metadata=json_object['usage']
            input,output,total=usage_metadata['prompt_tokens'],usage_metadata['completion_tokens'],usage_metadata['total_tokens']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(message.get('content'))
            if json:
                return AIMessage(loads(message.get('content')))
            if message.get('content'):
                return AIMessage(message.get('content'))
            else:
                tool_call=message.get('tool_calls')[0]['function']
                return ToolMessage(id=str(uuid4()),name=tool_call['name'],args=tool_call['arguments']) 
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    def stream(self, messages, json = False):
        pass