import { useRef, useState } from "react";

const ChatForm = ({ setChatHistory, generatebotResponse }) => {
  const inputRef = useRef();
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [isRecording, setIsRecording] = useState(false);

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (isRecording) {
      alert("Please stop the recording before sending a message.");
      return;
    }
    const userMessage = inputRef.current.value.trim();
    if (!userMessage) return;
    inputRef.current.value = "";
    setChatHistory((history) => [...history, { role: "user", text: userMessage }]);
  
    setTimeout(() => {
      generatebotResponse(userMessage);
    }, 1000);
  };
  

  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    } else {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice.webm');

        try {
          const res = await fetch("http://localhost:8000/upload", {
            method: "POST",
            body: formData,
          });

          const data = await res.json();
          const transcript = data.agent_response || "Could not transcribe";
          const fullAudioURL = `http://localhost:8000${data.audio_url}`;
        const audio = new Audio(fullAudioURL);
            audio.play().catch((e) => {
            console.error("Audio playback failed:", e);
            });
            
          return transcript
        } catch (err) {
          console.error("Upload failed", err);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    }
  };

  return (
    <form action="#" className="chat-form" onSubmit={handleFormSubmit}>
     <input
  ref={inputRef}
  type="text"
  placeholder="Message..."
  className="message-input"
  required
  disabled={isRecording}
/>

<button
  type="submit"
  className="material-symbols-rounded"
  disabled={isRecording}
>
  arrow_upward
</button>

      <button
        type="button"
        onClick={toggleRecording}
        className="material-symbols-rounded"
        style={{
          marginLeft: '8px',
          color: isRecording ? 'red' : 'black'
        }}
        title={isRecording ? "Stop Recording" : "Start Recording"}
      >
        mic
      </button>
    </form>
  );
};

export default ChatForm;
