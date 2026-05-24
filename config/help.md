# Aroxia: Complete User Documentation

## 1. Overview
Aroxia is a sophisticated multimodal Telegram companion designed to run seamlessly on Android or Cloud servers. She features Gemini Pro integration, local fallback (LFM-2), and cross-device synchronization.

## 2. Interaction Rules
- **Selective Response**: Aroxia only responds to `@Aroxia` mentions or direct replies in groups.
- **Bot Protocol**: She ignores other bots unless explicitly mentioned and enforces a 10s cooldown.
- **Context Awareness**: She looks back at the last 5-10 messages to understand the conversation situation.

## 3. Multimodal Features
- **Voice**: Supports Text-to-Speech (TTS) and understands incoming voice messages.
- **Image**: Can analyze and describe photos sent to her.
- **Stickers/GIFs**: Recognizes and reacts to stickers and animations.
- **Search**: Can perform Google searches and summarize URLs (YouTube/Wiki).

## 4. Modes & Settings
- **/mode [text|voice|both]**: Change how Aroxia responds.
- **Management GUI**: Use the "Status" tab to monitor CPU/RAM and the "Terminal" for hotfixes.

## 5. Deployment & Sync
- **Cloud Sync**: Uses Google Drive to sync memory between your phone and the server.
- **Dual Auth**: Supports both Developer API keys and Browser-based login.

## 6. Hotfix System
Use the internal terminal to edit files or reload modules without re-installing the app.
- `reload <module>`: Reloads a specific Python module.
- `gemini <query>`: Ask the built-in Gemini assistant for code help.

## 7. Troubleshooting
- **Rate Limited**: The Intelligence module will automatically pause the bot if limits are reached.
- **Offline**: If the cloud API fails, she automatically switches to the local LFM-2 model.
