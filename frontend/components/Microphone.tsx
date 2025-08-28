"use client"
import React, { useState, useRef } from "react";

export default function Microphone() {
  const [listening, setListening] = useState(false);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);

  const toggleMic = async () => {
    if (listening) {
      stopRecording();
    } else {
      await startRecording();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioCtx = new AudioContext();
      audioCtxRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      await audioCtx.audioWorklet.addModule("linear-pcm-processor.js");
      const audioWorkletNode = new AudioWorkletNode(audioCtx, "linear-pcm-processor");
      workletNodeRef.current = audioWorkletNode;

      source.connect(audioWorkletNode);

      const chunkBuffer: Int16Array[] = [];

      audioWorkletNode.port.onmessage = (e: MessageEvent<Int16Array>) => {
        if (e.data && e.data.length > 0) {
          chunkBuffer.push(e.data);
        }
      };

      setListening(true);
      console.log("Recording started for 10s...");

      // Stop after 10s
      setTimeout(async () => {
        audioWorkletNode.disconnect();
        source.disconnect();
        audioCtx.close();
        setListening(false);

        // merge
        if (chunkBuffer.length > 0) {
          const totalLength = chunkBuffer.reduce((sum, c) => sum + c.length, 0);
          const merged = new Int16Array(totalLength);
          let offset = 0;
          chunkBuffer.forEach((c) => {
            merged.set(c, offset);
            offset += c.length;
          });

          // send
          const blob = new Blob([merged.buffer], { type: "application/octet-stream" });
          const res = await fetch("http://localhost:5000/api/v1/audiodna", {
            method: "POST",
            headers: { "Content-Type": "application/octet-stream" },
            body: blob,
          });


          const data = await res.json();
          console.log("🎶 Recognition result:", data);
        }
      }, 10000); // 10 seconds

    } catch (err) {
      console.error("Mic access denied:", err);
    }
  };

  const stopRecording = () => {
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
    }
    setListening(false);
    console.log("Recording stopped manually");
  };

  return (
    <div className="flex flex-col items-center justify-center">
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
        {listening ? "Recording 10s..." : "Tap to Start"}
      </p>
    </div>
  );
}
