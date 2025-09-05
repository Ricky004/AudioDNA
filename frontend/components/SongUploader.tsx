"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

export default function SongUploader() {
  const [url, setUrl] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const res = await fetch("http://localhost:5000/api/v1/get-song-info", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      })

      const data = await res.json()

      if (data.status === "ok") {
        toast.success("✅ Song Uploaded", {
          description: `${data.song} by ${data.artists.join(", ")}`,
          className: "text-black dark:text-white",
        })
      } else {
        toast.error("❌ Upload Failed", {
          description: data.message || "Something went wrong.",
          className: "text-black dark:text-white",
        })
      }
    } catch (err) {
      toast.error("❌ Upload Failed", {
        description: String(err),
        className: "text-black dark:text-white",
      })
    }
  }

  return (
    <div className="p-4 flex flex-col items-center justify-center">
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <Input
          type="text"
          placeholder="Paste Spotify link here"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <Button type="submit" className="bg-green-700">Upload</Button>
      </form>
    </div>
  )
}
