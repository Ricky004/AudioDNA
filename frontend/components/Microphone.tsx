"use client"
import React, { useState, useRef } from "react";

export default function Microphone() {
  const [listening, setListening] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const toggleMic = async () => {
    if (listening) {
      mediaRecorderRef.current?.stop();
      setListening(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioCtx = new AudioContext()
        const source = audioCtx.createMediaStreamSource(stream)
        await audioCtx.audioWorklet.addModule("./lib/linear-pcm-processor.js")
        const audioWorkletNode = new AudioWorkletNode(audioCtx, "linear-pcm-processor")

        source.connect(audioWorkletNode)
        // Mic play back is off
        // audioWorkletNode.connect(audioCtx.destination) 

        let chunkBuffer: Int16Array[] = []

        // Receive PCM chunks from the processor
        audioWorkletNode.port.onmessage = async (e: MessageEvent<Int16Array>) => {
          if (e.data && e.data.length > 0) {
            chunkBuffer.push(e.data)
          }
        }

        setInterval(async () => {
          if (chunkBuffer.length > 0) {
            const totalLength = chunkBuffer.reduce((sum, c) => sum + c.length, 0)
            const merged = new Int16Array(totalLength)
            let offset = 0
            chunkBuffer.forEach((c) => {
              merged.set(c, offset)
              offset += c.length
            })

            // send to backend
            const blob = new Blob([merged.buffer], {type: "application/octet-stream"});
            await fetch("http://localhost:5000/api/v1/audiodna", {
              method: "POST",
              headers: {
                "Content-Type": "application/octet-stream",
              },
              body: blob,
            });

            chunkBuffer = [] // clear buffer
          }

        }, 2000)

        setListening(true);
      } catch (err) {
        console.error("Mic access denied:", err);
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <button
        onClick={toggleMic}
        className={`
          relative w-28 h-28 rounded-full flex items-center justify-center
          ${listening ? "bg-red-500 animate-pulse" : "bg-blue-500"}
          shadow-2xl transition-all duration-300 ease-in-out
        `}
      >
        <span className="text-3xl">🎤</span>
      </button>
      <p className="mt-6 text-lg">
        {listening ? "Listening & Sending..." : "Tap to Start"}
      </p>
    </div>
  );
}
