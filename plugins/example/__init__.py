"""
Example Plugin for WolfPy

This is a demonstration plugin that shows how to create and integrate
plugins with the WolfPy framework.
"""

from wolfpy.core.response import Response


def setup(app):
    """
    Setup the example plugin with the WolfPy app.
    
    Args:
        app: WolfPy application instance
    """
    print("🔌 Loading Example Plugin...")
    
    # Register plugin routes
    @app.route('/example')
    def example_home(request):
        """Example plugin home page."""
        return Response("""
        <html>
        <head>
            <title>Example Plugin</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .plugin-header { color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
                .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .code { background: #e9ecef; padding: 10px; border-radius: 3px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h1 class="plugin-header">🔌 Example Plugin</h1>
            <p>Welcome to the WolfPy Example Plugin! This demonstrates how plugins work.</p>
            
            <div class="feature">
                <h3>📋 Plugin Features</h3>
                <ul>
                    <li>Custom routes and endpoints</li>
                    <li>API integration</li>
                    <li>Template rendering</li>
                    <li>Database operations</li>
                    <li>Middleware integration</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🌐 Available Endpoints</h3>
                <ul>
                    <li><a href="/example">/example</a> - This page</li>
                    <li><a href="/example/api/info">/example/api/info</a> - Plugin API info</li>
                    <li><a href="/example/api/data">/example/api/data</a> - Sample data API</li>
                    <li><a href="/example/demo">/example/demo</a> - Interactive demo</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>💻 Plugin Code</h3>
                <div class="code">
def setup(app):<br>
&nbsp;&nbsp;&nbsp;&nbsp;@app.route('/example')<br>
&nbsp;&nbsp;&nbsp;&nbsp;def example_home(request):<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return "Hello from plugin!"
                </div>
            </div>
            
            <p><a href="/">← Back to Home</a> | <a href="/docs/plugins">📚 Plugin Documentation</a></p>
        </body>
        </html>
        """)
    
    @app.route('/example/api/info')
    def example_api_info(request):
        """Plugin API information endpoint."""
        return Response.json({
            'plugin': 'example',
            'version': '1.0.0',
            'status': 'active',
            'description': 'Example plugin for WolfPy framework',
            'endpoints': [
                '/example',
                '/example/api/info',
                '/example/api/data',
                '/example/demo'
            ],
            'features': [
                'custom_routes',
                'api_endpoints',
                'json_responses',
                'html_templates'
            ]
        })
    
    @app.route('/example/api/data')
    def example_api_data(request):
        """Sample data API endpoint."""
        # Simulate some data processing
        sample_data = [
            {'id': 1, 'name': 'Item 1', 'value': 100},
            {'id': 2, 'name': 'Item 2', 'value': 200},
            {'id': 3, 'name': 'Item 3', 'value': 300},
        ]
        
        # Support filtering
        filter_name = request.args.get('filter')
        if filter_name:
            sample_data = [item for item in sample_data if filter_name.lower() in item['name'].lower()]
        
        return Response.json({
            'data': sample_data,
            'count': len(sample_data),
            'plugin': 'example',
            'timestamp': __import__('time').time()
        })
    
    @app.route('/example/demo')
    def example_demo(request):
        """Interactive demo page."""
        return Response("""
        <html>
        <head>
            <title>Example Plugin Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .demo-section { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 5px; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #0056b3; }
                #output { background: #e9ecef; padding: 15px; border-radius: 3px; margin-top: 10px; min-height: 50px; }
                input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🔌 Example Plugin Demo</h1>
            
            <div class="demo-section">
                <h3>📡 API Testing</h3>
                <p>Test the plugin's API endpoints:</p>
                <button onclick="testAPI('/example/api/info')">Get Plugin Info</button>
                <button onclick="testAPI('/example/api/data')">Get Sample Data</button>
                <input type="text" id="filter" placeholder="Filter data...">
                <button onclick="testAPIWithFilter()">Filter Data</button>
                <div id="output">Click a button to test the API...</div>
            </div>
            
            <div class="demo-section">
                <h3>🔧 Plugin Features</h3>
                <ul>
                    <li>✅ Route registration</li>
                    <li>✅ JSON API responses</li>
                    <li>✅ HTML template rendering</li>
                    <li>✅ Request parameter handling</li>
                    <li>✅ Plugin lifecycle management</li>
                </ul>
            </div>
            
            <p><a href="/example">← Back to Plugin Home</a></p>
            
            <script>
                function testAPI(endpoint) {
                    fetch(endpoint)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('output').innerHTML = 
                                '<strong>Response from ' + endpoint + ':</strong><br><pre>' + 
                                JSON.stringify(data, null, 2) + '</pre>';
                        })
                        .catch(error => {
                            document.getElementById('output').innerHTML = 
                                '<strong>Error:</strong> ' + error.message;
                        });
                }
                
                function testAPIWithFilter() {
                    const filter = document.getElementById('filter').value;
                    const endpoint = '/example/api/data' + (filter ? '?filter=' + encodeURIComponent(filter) : '');
                    testAPI(endpoint);
                }
            </script>
        </body>
        </html>
        """)
    
    # Register plugin hooks (if needed)
    if hasattr(app, 'plugin_manager') and app.plugin_manager:
        app.plugin_manager.register_hook('plugin_loaded', on_plugin_loaded)
    
    print("✅ Example Plugin loaded successfully!")
    return True


def teardown(app):
    """
    Cleanup the example plugin.
    
    Args:
        app: WolfPy application instance
    """
    print("🔌 Unloading Example Plugin...")
    # Perform any cleanup here
    # Note: Routes are automatically cleaned up by the framework


def on_plugin_loaded(plugin_name):
    """Hook callback when a plugin is loaded."""
    if plugin_name != 'example':
        print(f"📦 Example plugin noticed that '{plugin_name}' was loaded")


# Plugin metadata
__version__ = "1.0.0"
__author__ = "WolfPy Team"
__description__ = "Example plugin demonstrating WolfPy plugin capabilities"
