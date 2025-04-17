import React, { useState } from 'react';
import './App.css';

function App() {
  const [movieName, setMovieName] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const fetchRecommendations = async () => {
    if (!movieName) return;

    setLoading(true);
    setShowResults(false); // Hide old results while loading

    try {
      const response = await fetch(`http://localhost:8000/recommend/${movieName}`);
      const data = await response.json();
      setRecommendations(data);
      setShowResults(true); // Show results after fetching
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setRecommendations(["⚠️ Failed to fetch recommendations."]);
      setShowResults(true);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <h1>🎬 Movie Recommender</h1>

      <div className="input-container">
        <input
          type="text"
          value={movieName}
          onChange={(e) => setMovieName(e.target.value)}
          placeholder="Enter a movie name..."
        />
        <button onClick={fetchRecommendations}>Get Recommendations</button>
      </div>

      <div className={`recommendation-box ${showResults ? 'fade-in' : ''}`}>
        {loading ? (
          <p className="loading">Loading...</p>
        ) : (
          showResults && (
            <ul>
              {recommendations.map((movie, index) => (
                <li key={index}>{movie}</li>
              ))}
            </ul>
          )
        )}
      </div>
    </div>
  );
}

export default App;
