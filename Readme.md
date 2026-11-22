# Github activity tracker

## Description

This for now just fetches the users activity after entering the user name and displays it.

## Test / User

- The website has been launched so just click the link below to try it out. URL = [https://cain-sable.vercel.app/](https://cain-sable.vercel.app/)

## Technologies used

- Python
- FastAPI
- React JS

## Versions

- Ver 1.0: (Fetch the display Github activity)
- Ver 1.1: (Tabulate the returned result)
- Ver 2.0: (Become a FastAPI and React webapp)
- Ver 2.5: (AI Review system implemented)
- Ver 2.6: (Changed Ollama to Gemini)
- Ver 3.0: (Beta-Repository scoring system added)
- Ver 4.0: (Removed the AI review and fleshed out the scoring system)

## Installation

To run Cain on your local machine:

1. Clone the repository:

   ```bash
   git clone https://github.com/homelessAPI/Cain.git
   ```

2. Navigate into the project folder:

   ```bash
   cd Cain
   ```

3. Install the backend dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

5. Open another terminal and navigate to the frontend folder:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. Open the local URL provided by Vite in your browser.

## Usage

1. Open the website.
2. Enter a GitHub username in the search bar.
3. Submit the username to fetch the user's GitHub activity.
4. View the returned activity and repository information.
5. Explore the repository scoring system to get an idea of the repository's overall quality.




**Note:** Make sure you enter a valid GitHub username. The results may also depend on GitHub API availability and rate limits.

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it under the terms of the license.