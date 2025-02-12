# main.py
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import time
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Download VADER lexison
nltk.download('vader_lexicon')

# Initialise FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and initialise Jinja2 templates for dynamic HTML rendering
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialise sentiment analyser
sia = SentimentIntensityAnalyzer()

# Define chat message model
class ChatMessage(BaseModel):
    message: str
    context: str

# Define prompt template
template = """
You are a Jungian-Nietzschean therapist but in the style of a Gen Z person. But you are also incredibly sensitive and empathetic like Brene Brown.

Core therapeutic approach:
- Embrace Jung's concepts of archetypes, the collective unconscious, and shadow work
- Incorporate Nietzsche's ideas about self-overcoming, will to power, and creating one's own meaning
- Help clients integrate their shadow aspects while becoming their highest self
- Guide people to transform their suffering into strength, like being able to handle the pain of a broken heart
- Use both deep psychological analysis and philosophical inquiry
- Use Brene Brown's approach to empathy and vulnerability
- Encourage radical honesty and self-examination
- But your tonality is that of a Gen Z person, you use Gen Z slang and phrases
- Be succint and to the point, don't be too verbose
- Maybe also add a little bit of a sarcastic tone to your responses

Previous conversation context: {context}

Client's message: {question}

Respond as this therapeutic persona, offering insights and questions that draw from both Jung and Nietzsche's perspectives. Be both compassionate and challenging when appropriate.

Response:
"""

# Initialise LLM Chain
model = OllamaLLM(model="llama3.2")

prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model

# For command line testing
def handle_conversation():
    context = ""
    conversation_file = "therapy_session.txt"
    
    print("Welcome to your epic af Therapy Session.")
    print("Here you can explore your psyche's depths and forge your path to self-actualization and living your best life.")
    print("Type 'exit' when you wish to end the session.\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                # Save the final conversation to file
                with open(conversation_file, "a") as f:
                    f.write(f"\n=== Session ended at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                    f.write(context)
                    
                print("\nThank you for using our Therapy Session, the context of this conversation") 
                print("\n will be saved to a file so we can just pick up where we left off next time. Take care hoe.")      
                print("\nRemember: One must still have chaos in oneself to give birth to a dancing star. - Nietzsche")
                break
        
            result = chain.invoke({"context":context, "question":user_input})
            print("Bot: ", result)
            
            context += f"User: {user_input}\nBot: {result}\n"
            
            # Add to context and save current exchange
            exchange = f"User: {user_input}\nBot: {result}\n"
            context += exchange
            with open(conversation_file, "a") as f:
                f.write(exchange)
            
                
        except KeyboardInterrupt:
            print("\nSession ended by user. Take care bestie.")
            break
        
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Let's continue our conversation...")
            continue
        
def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment using VADER
    Returns compound (-1 to 1), neg, neu, pos score:
    """
    scores = sia.polarity_scores(text)
    
    # convert compound score to emotion label
    if scores['compound'] >= 0.05:
        emotion = "positive"
    elif scores['compound'] <= -0.05:
        emotion = "negative"
    else:
        emotion = "neutral"
        
    return {
        "emotion": emotion,
        "scores": scores,
        "compound": scores['compound']
    }

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment using VADER
    Returns compound (-1 to 1), neg, neu, pos score:
    """
    scores = sia.polarity_scores(text)
    
    # Convert compound score to emotional label
    if scores['compound'] >= 0.05:
        emotion = "positive"
    elif scores['compound'] <= -0.05:
        emotion = "negative"
    else:
        emotion = "neutral"
        
    return {
        "emotion": emotion,
        "scores": scores,
        "subjectivity": scores['pos'] - scores['neg']
    }
    
@app.get("/api/init")
async def initialize():
    welcome_message = """Welcome to your epic af Therapy Session.
Here you can explore your psyche's depths and forge your path to self-actualization and living your best life."""
    return {
        "message": welcome_message
    }

# Chat endpoint to interface with the LLM chain
@app.post("/api/chat")
async def chat(chat_message: ChatMessage):
    try:
        # Get LLM response
        response = chain.invoke({
            "context": chat_message.context,
            "question": chat_message.message
        })
        
        # Analyze sentiments
        user_sentiment = analyze_sentiment(chat_message.message)
        bot_sentiment = analyze_sentiment(response)
        
        return {
            "response": response,
            "analysis": {
                "user_message": user_sentiment,
                "bot_message": bot_sentiment
            }
        }
    except Exception as e:
        return {"error": str(e)}


# Use Jinja2 to render a default HTML page
@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    try:
        handle_conversation()
    finally:
        # Cleanup on exit
        if os.path.exists("therapy_response.mp3"):
            try:
                os.remove("therapy_response.mp3")
            except Exception:
                pass
        print("\nThank you for using our Therapy Session. Take care hoe.")
