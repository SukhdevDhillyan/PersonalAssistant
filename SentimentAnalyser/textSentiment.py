import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class TextSentiment:
    def __init__(self):
        nltk.download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()

    def analyse(self, text):
        """
        Analyzes the sentiment of a given text conversation.
        :param text: String input
        :return: Dictionary with sentiment scores and label
        """
        sentiment_scores = self.analyzer.polarity_scores(text)
        sentiment_label = self._interpret_sentiment(sentiment_scores['compound'])
        return {
            "mode": "text",
            "input": text,
            "scores": sentiment_scores,
            "sentiment": sentiment_label
        }

    def _interpret_sentiment(self, compound_score):
        """Converts compound score into human-readable sentiment."""
        if compound_score >= 0.05:
            return "Positive"
        elif compound_score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
