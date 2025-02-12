import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

type Message = {
    sender: 'Patient' | 'Therapist';
    text: string;
}

const Chat: React.FC = () => {
    const [message, setMessage] = useState<string>('');
    const [messages, setMessages] = useState<Message[]>([
        { 
            sender: 'Therapist', 
            text: 'Welcome to the AI Therapist chat bro\nYour backend is up and running' }
    ]);
    const [response, setResponse] = useState<string>('');
    const conversationRef = useRef<HTMLDivElement>(null);
    const conversationEndRef = useRef<HTMLDivElement>(null);
    
    useEffect(() => {
        conversationEndRef.current?.scrollIntoView({ 
            behavior: 'smooth' 
        });
    }, [messages]);

    const handleSend = async () => {
        if (!message.trim()) return;

        const newPatientMessage: Message = {
            sender: 'Patient',
            text: message
        };
        setMessages(prev => [...prev, newPatientMessage]);

        const payload = {
            message,
            context: messages.map(m => `${m.sender}: ${m.text}`).join('\n')
        };
        
        setMessage('');

        try {
            const res = await fetch('http://127.0.0.1:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            
            if (data.response) {
                const newTherapistMessage: Message = { sender: 'Therapist', text: data.response };
                setMessages(prev => [...prev, newTherapistMessage]);
                setResponse(data.response);
            } else {
                setResponse('Error: no response received.');
            }
        } catch (error) {
            console.error('Error sending message', error);
            setResponse('Error: failed to send message.');
        }
        setMessage('');
    };

    return (
        <div className="chatContainer">
            <h2>Chat with the somewhat attractive AI Therapist</h2>
            <div className="conversation">
                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`messageBubble ${msg.sender === 'Patient' ? 'userMessage' : 'botMessage'}`}
                    >
                        {msg.text}
                    </div>
                ))}
            </div>
            <div className="MessageBoxContainer">
                <input
                    type="text"
                    placeholder="Express the inner turmoil of your soul here..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    className="messageBox"
                />
                <button onClick={handleSend} className="sendButton" aria-label="Send message">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="currentColor"
                        width="28"
                        height="28"
                        viewBox="0 0 24 24"
                    >
                        <path d="M2.01 21L23 12 2.01 3v7l15 2-15 2z" />
                    </svg>
                </button>
            </div>
            <div className="latestResponse">
                <strong>Latest Response:</strong> {response}
            </div>
        </div>
    );
};

export default Chat;
        