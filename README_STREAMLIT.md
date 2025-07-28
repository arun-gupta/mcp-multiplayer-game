# 🎮 MCP Multiplayer Game - Streamlit Version

A clean, Python-based interface for the Multi-Agent Communication Protocol (MCP) Tic Tac Toe game using Streamlit.

## 🚀 Quick Start

### Option 1: Automatic Setup
```bash
python run_streamlit.py
```

### Option 2: Manual Setup
1. **Start the API server** (in one terminal):
   ```bash
   python main.py
   ```

2. **Install Streamlit dependencies** (in another terminal):
   ```bash
   pip install -r requirements_streamlit.txt
   ```

3. **Start the Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

## ✨ Features

### 🎮 Game Tab
- **Interactive Tic Tac Toe board** with clickable cells
- **Real-time game status** showing current player and move number
- **Move history** with detailed player and AI moves
- **Game controls** for new game and refresh

### 🤖 Agents Tab
- **Agent information** showing Scout, Strategist, and Executor
- **Current model assignments** for each agent
- **Agent status** and role descriptions

### 📡 MCP Logs Tab
- **Real-time MCP protocol logs** showing agent communication
- **JSON data display** for each message
- **Timestamp tracking** for all protocol exchanges

### 📊 Metrics Tab
- **MCP message count** and total cost tracking
- **Game duration** and average response times
- **LLM cost breakdown** with visual charts
- **Agent response time** comparisons

### 🔄 Models Tab
- **Hot-swappable LLM models** for each agent
- **Cost information** for each model
- **Availability status** and model switching
- **Real-time model updates**

## 🎯 Advantages Over HTML/JS Version

✅ **No JavaScript syntax errors** - Everything is Python  
✅ **Cleaner codebase** - No complex string concatenations  
✅ **Better maintainability** - Streamlit handles the UI complexity  
✅ **Professional appearance** - Built-in styling and components  
✅ **Easy deployment** - Streamlit Cloud ready  
✅ **Real-time updates** - Automatic refresh and state management  
✅ **Better error handling** - Clear error messages and recovery  

## 🔧 Technical Details

- **Backend**: FastAPI with all existing MCP logic preserved
- **Frontend**: Streamlit with Python-based UI components
- **Communication**: HTTP requests to the existing API endpoints
- **State Management**: Streamlit session state and automatic refresh
- **Styling**: Custom CSS for game-like appearance

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: API Server
python main.py

# Terminal 2: Streamlit App
streamlit run streamlit_app.py
```

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Deploy with the command: `streamlit run streamlit_app.py`

## 📁 File Structure

```
mcp-multiplayer-game/
├── main.py                    # FastAPI backend (existing)
├── streamlit_app.py           # Streamlit frontend (new)
├── run_streamlit.py           # Launcher script (new)
├── requirements_streamlit.txt # Streamlit dependencies (new)
├── README_STREAMLIT.md        # This file (new)
└── ... (existing files)
```

## 🎮 How to Play

1. **Start the application** using the instructions above
2. **Click any empty cell** on the Tic Tac Toe board
3. **Watch the AI agents** communicate using MCP protocol
4. **Explore the tabs** to see agents, logs, metrics, and models
5. **Switch models** in the Models tab to experiment with different LLMs
6. **Monitor performance** in the Metrics tab

## 🔍 MCP Protocol Visualization

The Streamlit interface provides a clear view of the Multi-Agent Communication Protocol:

- **Scout Agent** (🔍): Observes the game state
- **Strategist Agent** (🧠): Creates plans and strategies  
- **Executor Agent** (⚡): Executes the chosen moves

Each agent communicates through structured JSON messages, which are displayed in real-time in the MCP Logs tab.

## 🎯 Next Steps

- **Deploy to Streamlit Cloud** for easy sharing
- **Add more game types** beyond Tic Tac Toe
- **Enhance metrics visualization** with more charts
- **Add agent conversation history** tracking
- **Implement model performance comparison** tools

---

**Enjoy the MCP Multiplayer Game! 🎮✨** 