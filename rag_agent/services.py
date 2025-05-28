from fastapi import  HTTPException
from openai import OpenAI
from rag_agent.llm import retriever
import os


past_conversation = []
def retriever_query(request):
    openai_key=os.getenv("OPENAI_AI_KEY")
    client = OpenAI(api_key=openai_key)
    try:
        retrieved_results = retriever(request)
        context = "\n".join(retrieved_results["documents"][0])
        formatted_history = []
        if past_conversation:
            for msg in past_conversation[-5:]:  
                formatted_history.append({"role": msg["role"], "content": msg["text"]})

        formatted_history.append({"role": "user", "content": request})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a assistant agent. Answer the user queries with given knowledge base and implement a feedback mechanism if user queries is not available in the knowledge base"},
                {"role": "system", "content": f"Context: {context}"},
                *formatted_history
            ],
            temperature=0.5,
        )
        answer = response.choices[0].message.content
        
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))