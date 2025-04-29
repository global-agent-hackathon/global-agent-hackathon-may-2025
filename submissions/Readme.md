## Overview of the idea

ChessMates AutoAgent is an AI-powered automation agent designed to enhance the ChessMates platform by generating and publishing high-quality chess-related content daily. The agent autonomously creates engaging chess puzzles and shares trending news from the chess world, keeping the community informed and engaged without manual intervention.

## Explanation of how it works



## Technologies/tools used



## All setup instructions (API keys, signups, etc.)

- refer to the .env_example file and create a .env file with appropriate API keys:

GEMINI_API_KEY (your gemini api key)
SARVAM_API_KEY (you sarvam ai api key)
DB_USER (your postgresql db user)
DB_PASSWORD (your postgresql db password)
DB_HOST (your postgresql db host name)
DB_PORT (your postgresql db port number)
DB_NAME (your postgresql db name)

FETCH_NEWS_API_URL=http://127.0.0.1:8000/news
FETCH_PUZZLE_API_URL=http://127.0.0.1:8000/puzzle
POST_NEWS_API_URL=https://chessmates-pr.vercel.app/api/create-news
POST_PUZZLE_API_URL=https://chessmates-pr.vercel.app/api/create-puzzle

- Make sure you have python version 3.11 along with postgres and pgadmin up and running 
- The default stockfish engine is for mac os, the windows and linux ones are already installed in the [stockfish directory](stockfish). Rename the required engine to stockfish and rename the others to something else, so as to not clash names

- setup a virtual environment :
``` python -m venv myenv ```

- activate the virtual environment:
``` source myenv/bin/activate ```

- install requirements:
``` pip install -r requirements.txt ```

- start the fastapi server:
``` uvicorn main:app --reload ```

- in a new terminal outside the environment, install packages and start the cron jobs:
``` npm install ```
``` npm run start ```



