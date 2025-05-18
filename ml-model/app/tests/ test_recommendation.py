import pytest

@pytest.fixture
def mock_similarity_data():
    return [
        [1.0, 0.92, 0.31],
        [0.92, 1.0, 0.45],
        [0.31, 0.45, 1.0]
    ]

@pytest.fixture
def mock_titles():
    return {0: "Inception", 1: "Interstellar", 2: "The Prestige"}

def get_top_recommendations(index, similarity_matrix, titles, top_n=2):
    scores = list(enumerate(similarity_matrix[index]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_indices = [i for i, _ in scores if i != index][:top_n]
    return [titles[i] for i in top_indices]

def test_recommendation_logic(mock_similarity_data, mock_titles):
    results = get_top_recommendations(0, mock_similarity_data, mock_titles)
    assert "Interstellar" in results
    assert len(results) == 2