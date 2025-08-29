"use client"
import { useState } from "react";

export default function SongUploader() {
  const [url, setUrl] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await fetch("https://audiodna.onrender.com/api/v1/get-song-info", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });
  };

  return (
    <div className="p-4 flex flex-col items-center justify-center">
      <form onSubmit={handleSubmit} className="space-x-2">
        <input
          type="text"
          placeholder="Paste Spotify link here"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="border p-2 rounded"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Upload
        </button>
      </form>
    </div>
  );
}
