import React, { useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { clearStoredTokens } from "../utils/auth";

const SummaryAIPage = () => {
  const { videoId } = useParams<{ videoId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { title } = location.state as { title: string };
  const [prompt, setPrompt] = useState("");
  const [summary, setSummary] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      console.error("Token is missing.");
      navigate("/");
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/api/summarize_comments",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ video_id: videoId, prompt }),
        }
      );

      const data = await response.json();
      if (response.ok) {
        setSummary(data.summary);
      } else {
        console.error("Failed to fetch summary:", data.detail);
        if (data.detail.includes("insufficient authentication scopes")) {
          clearStoredTokens();
          navigate("/login", {
            state: {
              message: "Please log in again to grant necessary permissions.",
            },
          });
        }
      }
    } catch (error) {
      console.error("Error fetching summary:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="flex flex-col items-center p-8">
      <h1 className="text-2xl font-bold mb-4">AI Summary for Video: {title}</h1>
      <Textarea
        placeholder="What do you want to know about the comments on this video?"
        className="w-full max-w-2xl mb-4"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <Button
        className="bg-blue-500 text-white"
        onClick={handleSubmit}
        disabled={isLoading}
      >
        {isLoading ? "Processing..." : "Submit"}
      </Button>
      {summary && (
        <div className="w-full max-w-2xl mt-6 p-4 border border-gray-300 rounded">
          <h2 className="text-xl font-semibold mb-2">Summary</h2>
          <p className="text-gray-700">{summary}</p>
        </div>
      )}
      <Button
        className="bg-gray-500 text-white mt-4"
        onClick={() => navigate("/")}
      >
        Back to Videos
      </Button>
    </section>
  );
};

export default SummaryAIPage;
