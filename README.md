# Data Analyst Agent API

An AI-powered data analyst agent that can source, prepare, analyze, and visualize data using Large Language Models. This Flask application provides an API endpoint that accepts data analysis tasks and returns comprehensive analysis results within 3 minutes.

## Features

- **Task Interpretation**: Uses LLMs to understand and plan data analysis tasks
- **Statistical Analysis**: Performs comprehensive statistical analysis on datasets
- **Data Visualization**: Generates charts, graphs, and plots
- **Insight Generation**: Provides AI-generated insights and interpretations
- **Recommendations**: Offers actionable recommendations based on analysis
- **Multiple Data Formats**: Supports CSV, JSON, Excel, and text files

## API Endpoints

### `GET /`
Returns API information and available endpoints.

### `POST /api/`
Submit a data analysis task for processing.

**Request Methods:**
1. **JSON Request:**
   ```bash
   curl -X POST https://data-analyst-agent-tds.vercel.app/api \
     -H "Content-Type: application/json" \
     -d '{"task": "Analyze sales data and provide insights"}'
   ```

2. **File Upload:**
   ```bash
   curl -X POST https://data-analyst-agent-tds.vercel.app/api \
     -F "file=@question.txt"
   ```

3. **Text Data:**
   ```bash
   curl -X POST https://data-analyst-agent-tds.vercel.app/api \
     -d "Analyze customer behavior patterns and recommend optimization strategies"
   ```

### `GET /about`
Returns detailed information about the API capabilities.

## Environment Variables

Before deploying, you need to set up the following environment variables:

- `OPENAI_API_KEY`: Your AI Pipe Token
- `OPENAI_BASE_URL`: `https://aipipe.org/openai/v1`

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY=your_aipipe_token
   export OPENAI_BASE_URL=https://aipipe.org/openai/v1
   ```

3. **Run locally with Vercel CLI:**
   ```bash
   npm i -g vercel
   vercel dev
   ```

4. **Or run with Flask directly:**
   ```bash
   python api/index.py
   ```

Your application will be available at `http://localhost:3000`.

## Deployment on Vercel

1. **Clone this repository**
2. **Set environment variables in Vercel dashboard:**
   - `OPENAI_API_KEY`: Your AI Pipe Token
   - `OPENAI_BASE_URL`: `https://aipipe.org/openai/v1`
3. **Deploy using the button above or Vercel CLI:**
   ```bash
   vercel --prod
   ```

## Architecture

The application follows a modular architecture:

- **Flask App**: Main application framework
- **DataAnalyst Class**: Core analysis engine
- **LLM Integration**: Uses AI Pipe for task interpretation and insight generation
- **Data Processing**: Pandas for data manipulation
- **Visualization**: Matplotlib and Seaborn for charts
- **API Layer**: RESTful endpoints for task submission

## Response Time

The API is designed to respond within 3 minutes for most analysis tasks. Complex analyses may take longer but will always provide status updates.

## Error Handling

The API includes comprehensive error handling and will return detailed error messages and stack traces for debugging purposes.

## License

This project is open source and available under the MIT License.