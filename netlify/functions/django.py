import os
import sys
from urllib.parse import unquote

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')

# Configure Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse

# Get the WSGI application
application = get_wsgi_application()

def handler(event, context):
    """
    Netlify Function handler for Django application
    """
    try:
        # Extract HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Handle query parameters
        query_params = event.get('queryStringParameters') or {}
        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        
        # Get headers
        headers = event.get('headers', {})
        
        # Get body
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            import base64
            body = base64.b64decode(body)
        
        # Create a minimal WSGI environ
        environ = {
            'REQUEST_METHOD': http_method,
            'PATH_INFO': unquote(path),
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)) if body else '0',
            'SERVER_NAME': headers.get('host', 'localhost').split(':')[0],
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': body,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers to environ
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value
        
        # Call Django application
        response_data = []
        status = '200 OK'
        response_headers = []
        
        def start_response(status_code, headers):
            nonlocal status, response_headers
            status = status_code
            response_headers = headers
        
        response = application(environ, start_response)
        
        # Collect response data
        for data in response:
            if data:
                response_data.append(data)
        
        # Combine response data
        response_body = b''.join(response_data)
        
        # Convert headers to dict
        headers_dict = {}
        for header_name, header_value in response_headers:
            headers_dict[header_name] = header_value
        
        return {
            'statusCode': int(status.split()[0]),
            'headers': headers_dict,
            'body': response_body.decode(),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Internal Server Error</h1><p>{str(e)}</p>',
            'isBase64Encoded': False
        }

# For local development
if __name__ == '__main__':
    print("Django function handler loaded successfully!")
