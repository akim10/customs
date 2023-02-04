# Customs
This script takes data from custom League of Legends games and outputs them onto a Google Sheet.

## How to Use
1. Download [ReplayBook](https://github.com/fraxiinus/ReplayBook). This will let you download json files containing replay data from your saved League of Legends replays.

2. Use ReplayBook to export data as a json from each game into a folder (you can just export everything, or create a preset and only export desired fields if you want to keep file sizes small).

3. Setup [pygsheets](https://pygsheets.readthedocs.io/en/stable/authorization.html).

4. Create Google Sheets with titles that match the sheets being opened in the script.
Here are [some templates](https://drive.google.com/drive/folders/1DYUr2hkn-mtoWqRQ6WcIjmuk_pj9BeGc?usp=sharing) (copy them to your Drive) to start with that match the sheet names in the script.

5. Set the filepath (ctrl+F "path_to_json") to the folder containing the game data jsons from ReplayBook. (there's an example folder called "customs_data" with json files in it already)

6. Run 'python customs.py' in the project directory.
