# Overview
his is a fork of [Retrieval-based-Voice-Conversion-WebUI (RVC)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI).  
It was created as an experiment to pass user voice input to the [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) and then pass the response audio as input to RVC.  

# Install
The basic installation procedure is the same as RVC, but currently it has only been tested on Windows.  
For Windows users, please use the pre-built version available from [Releases](https://github.com/bruefire/RealtimeAPI-WithRVC/releases)  

# Usage
Run go-realtime-gpt.bat.  
The basic usage is the same as the GUI in go-realtime-gui.bat, but there are additional fields at the top for the API key and the initial prompt.  

![example](https://github.com/user-attachments/assets/ec94b4a7-2762-4767-98e7-49b853590449)
## API Key
The OpenAI API key is required. Create one from the OpenAI website and paste it into this field.  

## Initial Prompt
This is optional. If you have a prompt you'd like to use as initial instructions for the voice chat, enter it here.  

Press the start button in the bottom left to begin the voice chat.  
(As of October 15, 2024, API usage fees can be fairly high, so please be mindful of overuse.)  
