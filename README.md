# RD_FileGames

A collection of games created with **RD_FileGameBuilder** and playable with **RD_FileGameEngine**.

## Structure

Each game lives in its own subdirectory and follows the FILE_GAME data layout:

```
GAME_NAME/
  LEVELS/
    LEVEL_1/
      level_info.json
      SCENE_1/
        scene_info.json
        scene.png
        scene.md
  GUI/
    gui_layout.json
    OcrB2.ttf
  GAME_STATE/
    Default_Game_State.json
```

## Playing a Game

Install **RD_FileGameEngine** and place game folders inside `C:\FILE_GAMES\GAMES\`.
The engine will discover them automatically on launch.

## Creating a Game

Use **RD_FileGameBuilder** to author levels, scenes, and zones.
Save or export your project to `C:\FILE_GAMES\GAMES\` so the engine can find it.

## Assets

Binary assets (images, fonts, audio) are tracked with [Git LFS](https://git-lfs.github.com).
Run `git lfs install` before cloning if you haven't already:

```bash
git lfs install
git clone https://github.com/recluse-audio/RD_FileGames.git
```
