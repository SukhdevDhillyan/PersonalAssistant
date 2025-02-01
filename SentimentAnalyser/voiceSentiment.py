from textSentiment import TextSentiment

class VoiceSentiment:
    def __init__(self):
        self.text_analyser = TextSentiment()

    def analyse(self, audio_file):
        """
        Processes an audio file, converts it to text, and analyzes sentiment.
        :param audio_file: Path to audio file (WAV, FLAC, MP3)
        :return: Sentiment analysis result
        """
        pass
