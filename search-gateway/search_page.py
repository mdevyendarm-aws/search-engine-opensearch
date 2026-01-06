import json

def lambda_handler(event, context):
    """
    This function serves the Search Engine User Interface (HTML).
    It is triggered by the root path ('/') of your HTTP API.
    """
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Serverless Search Engine</title>
        <style>
            body { font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #f4f4f9; }
            .search-container { text-align: center; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 80%; max-width: 600px; }
            input[type="text"] { width: 70%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }
            button { padding: 10px 20px; border: none; background-color: #007bff; color: white; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #0056b3; }
            #results { margin-top: 20px; text-align: left; width: 100%; max-height: 300px; overflow-y: auto; }
            .result-item { padding: 10px; border-bottom: 1px solid #eee; }
        </style>
    </head>
    <body>
        <div class="search-container">
            <h1>Search Engine</h1>
            <input type="text" id="query" placeholder="Enter search term...">
            <button onclick="runSearch()">Search</button>
            <div id="results"></div>
        </div>

        <script>
            async function runSearch() {
                const query = document.getElementById('query').value;
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = 'Searching...';

                try {
                    // This calls the /search route you created in API Gateway
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ "searchTerm": query })
                    });

                    const data = await response.json();
                    
                    if (data.results && data.results.length > 0) {
                        resultsDiv.innerHTML = data.results.map(item => 
                            `<div class="result-item">${JSON.stringify(item)}</div>`
                        ).join('');
                    } else {
                        resultsDiv.innerHTML = 'No results found.';
                    }
                } catch (error) {
                    resultsDiv.innerHTML = 'Error fetching results. Check CORS or API logs.';
                    console.error('Search error:', error);
                }
            }
        </script>
    </body>
    </html>
    """

    # MANDATORY: HTTP APIs require a dictionary return with these keys
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*"  # Enables basic CORS support
        },
        "body": html_content
    }
