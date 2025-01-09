import React, { useState } from 'react';
import { Youtube, Star } from 'lucide-react';
import axios from 'axios';

import toast, { Toaster } from 'react-hot-toast';

function App() {
  const [url, setUrl] = useState('');
  const [videoData, setVideoData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Send the YouTube URL to the backend and return the summary text
  const sendPostRequest = async (url) => {
    const data = {
      youtube_url: url,
    };

    try {
      const response = await axios.post(' http://localhost:5173/summarize', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
     
      return response.data; // Assuming the response contains 'title', 'summary', and 'thumbnail'
    } catch (error) {
      toast.error("No Captions or Subtitles were found for this video.");
      console.error('Error:', error);
      
      return null; // Return null in case of error
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const data = await sendPostRequest(url); // Await the API response
      if (data) {
        setVideoData({
          title: data.title,
          summary: data.summary,
          thumbnail: data.thumbnail,
          url,
        });
      }
    } catch (error) {
      console.error('Error during API request:', error);
    } finally {
      setUrl('');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <header className="text-center mb-8">
        <Toaster />
          <h1 className="text-3xl font-bold text-gray-800 mb-2">

            YouTube Video Summarizer
          </h1>
          <p className="text-gray-600">Get quick summaries of any YouTube video</p>
        </header>

        <form onSubmit={handleSubmit} className="mb-12">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste a YouTube URL here..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 shadow-sm"
                required
              />
              <Youtube className="absolute right-3 top-3.5 h-5 w-5 text-gray-400" />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 shadow-sm font-medium"
            >
              {isLoading ? 'Generating...' : 'Generate Summary'}
            </button>
          </div>
        </form>

        {isLoading && (
          <div className="flex justify-center my-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600"></div>
          </div>
        )}

        {/* Display the current video title, summary, and thumbnail */}
        {videoData && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <img
                src={videoData.thumbnail}
                alt="Video Thumbnail"
                className="w-32 h-32 object-cover rounded-lg"
              />
              <div>
                <h3 className="text-lg font-semibold mb-2">{videoData.title}</h3>
                <a
                  href={videoData.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:text-green-700 font-medium"
                >
                  View Original Video
                </a>
              </div>
            </div>

            <p className="text-gray-600 mb-4">{videoData.summary}</p>

          
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
