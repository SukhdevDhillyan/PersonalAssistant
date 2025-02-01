from textSentiment import TextSentiment
from voiceSentiment import VoiceSentiment
from visualSentiment import VisualSentiment

class SentimentAnalyser:
    def __init__(self):
        self.text_analyser = TextSentiment()
        self.voice_analyser = VoiceSentiment()
        self.visual_analyser = VisualSentiment()

    def analyse(self, input_data, mode="text"):
        """
        Routes the input to the appropriate sentiment analysis module.
        
        :param input_data: Input data (text, audio file, or image)
        :param mode: "text", "voice", or "visual"
        :return: Sentiment analysis result
        """
        if mode == "text":
            return self.text_analyser.analyse(input_data)
        elif mode == "voice":
            return self.voice_analyser.analyse(input_data)
        elif mode == "visual":
            return self.visual_analyser.analyse(input_data)
        else:
            return {"error": "Invalid mode selected. Choose 'text', 'voice', or 'visual'."}
