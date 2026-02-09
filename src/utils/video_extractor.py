import re
import requests
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class VideoExtractor:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("VideoExtractor Class Initialized")

    def extract_video_id(self, url:str):
        try:
            if not url or not isinstance(url, str):
                raise CustomException("URL is empty or invalid")
            
            patterns = [
                r"(?:v=|\/)([0-9A-Za-z_-]{11})",               # Regular Long YT URL
                r"youtu\.be\/([0-9A-Za-z_-]{11})",             # Short YT URL
                r"youtube\.com\/shorts\/([0-9A-Za-z_-]{11})"   # Shorts YT URL
            ]

            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    self.logger.info(f"Extracted video ID : {video_id}")
                    return video_id
            raise CustomException("Couldn't find a match and video URL is not valid")
        
        except Exception as e:
            self.logger.error(f"Error while extracting user ID {str(e)}")
            raise CustomException("Error while extracting the video ID")
        

    def get_youtube_metadata(self, video_id:str):
        try:
            self.logger.info("Fetching the metadata")

            api_url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {"User-Agent":"Mozilla/5.0"}

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code != 200:
                self.logger.error(f"API call failed for {video_id}")
                raise CustomException(f"API call failed for {video_id}")
            
            html = response.text

            def extract(pattern, default=""):
                m = re.search(pattern, html)
                return m.group(1) if m else default
                
            title = extract(r'<meta property="og:title" content="([^"]+)"' , "Untitled Video")
            thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

            duration = int(extract(r'"lengthSeconds":"(\d+)"', 400))

            views = int(extract(r'"viewCount":"(\d+)"', 100))

            author = extract(r'"author":"([^"]+)"',"Unknown Creator")

            metadata={
                "title" : title,
                "thumbnail_url" : thumbnail,
                "duration" : duration,
                "views":views,
                "author":author,
                "platform": "Youtube",
                "video_id" : video_id
            }

            self.logger.info("Extracted metadata successfully..")
            return metadata
        
        except Exception as e:
            self.logger.error(f"Error while extracting metadata")
            raise CustomException("Error while extracting metadata")
        

    def get_video_metadata(self, url:str):
        try:
            self.logger.info(f"Processing URL {url}")

            video_id = self.extract_video_id(url)

            return self.get_youtube_metadata(video_id)

        except Exception as e:
            self.logger.error(f"Error while processing : {str(e)}")
            raise CustomException("Error while processing url",e)
        

### Helper Function
def get_video_metadata(url:str):
    extractor = VideoExtractor()
    return extractor.get_video_metadata(url)


            