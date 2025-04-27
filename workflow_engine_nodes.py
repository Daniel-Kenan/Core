from workflow_engine import register
from  datetime import datetime
import time
import json
import requests
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#                         REGISTER NODES BUSINESS LOGIC HANDLERS BELOW 
#   
#   Handlers registry: map node 'id' to its business-logic function  
#   Cross functional team can define how each node should behave in the app when it is executed in a workflow.
#   We can abstract the business logic from the node definition and put it in a separate file or remote server.   
#   
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
SIMULATE = True  # SIMULATES INSTEAD OF EXECUTING THE REAL BUSSINESS LOGIC TOS SAVE RSS
node_categories = [
    {
        'id': 'triggers',
        'name': 'Triggers',
        'iconKey': 'Clock',
        'nodes': [
            {'id': 'webhook', 'name': 'Webhook', 'type': 'trigger', 'description': 'Trigger workflow via HTTP request', 'iconKey': 'Share2'},
            {'id': 'schedule', 'name': 'Schedule', 'type': 'trigger', 'description': 'Trigger workflow on a schedule', 'iconKey': 'Calendar'},
            {'id': 'click', 'name': 'Manual Run', 'type': 'trigger', 'description': 'Trigger workflow manually', 'iconKey': 'Zap'},
            {'id': 'chat', 'name': 'Chat Message', 'type': 'trigger', 'description': 'Trigger on incoming chat message', 'iconKey': 'MessageSquare'},
            {'id': 'email', 'name': 'Email Received', 'type': 'trigger', 'description': 'Trigger when an email is received', 'iconKey': 'Mail'},
            {'id': 'form', 'name': 'Form Submission', 'type': 'trigger', 'description': 'Trigger on form submission', 'iconKey': 'FileInput'},
            {'id': 'database-change', 'name': 'Database Change', 'type': 'trigger', 'description': 'Trigger on database record changes', 'iconKey': 'Database'},
            {'id': 'interval', 'name': 'Timer Interval', 'type': 'trigger', 'description': 'Trigger at regular intervals', 'iconKey': 'Timer'},
        ],
    },
    {
        'id': 'apps',
        'name': 'Apps',
        'iconKey': 'Globe',
        'nodes': [
            {'id': 'http', 'name': 'HTTP Request', 'type': 'action', 'description': 'Make HTTP requests', 'iconKey': 'Globe'},
            {'id': 'email-send', 'name': 'Send Email', 'type': 'action', 'description': 'Send emails', 'iconKey': 'Mail'},
            {'id': 'database', 'name': 'Database', 'type': 'action', 'description': 'Query databases', 'iconKey': 'Database'},
            {'id': 'googlesheets', 'name': 'Google Sheets', 'type': 'action', 'description': 'Read/write Google Sheets data', 'iconKey': 'FileSpreadsheet'},
            {'id': 'file-operations', 'name': 'File Operations', 'type': 'action', 'description': 'Read/write files', 'iconKey': 'FileText'},
            {'id': 'sms', 'name': 'SMS Message', 'type': 'action', 'description': 'Send SMS messages', 'iconKey': 'Phone'},
            {'id': 'pdf', 'name': 'PDF Generator', 'type': 'action', 'description': 'Generate PDF documents', 'iconKey': 'FileCheck'},
            {'id': 'calendar', 'name': 'Calendar', 'type': 'action', 'description': 'Manage calendar events', 'iconKey': 'Calendar'},
        ],
    },
    {
        'id': 'flow',
        'name': 'Flow',
        'iconKey': 'Filter',
        'nodes': [
            {'id': 'if', 'name': 'IF Condition', 'type': 'logic', 'description': 'Conditional branching', 'iconKey': 'Filter'},
            {'id': 'switch', 'name': 'Switch', 'type': 'logic', 'description': 'Multiple path branching', 'iconKey': 'SplitSquareVertical'},
            {'id': 'loop', 'name': 'Loop Over Items', 'type': 'logic', 'description': 'Iterate over items', 'iconKey': 'Repeat'},
            {'id': 'merge', 'name': 'Merge', 'type': 'logic', 'description': 'Merge branches', 'iconKey': 'Merge'},
            {'id': 'delay', 'name': 'Delay', 'type': 'logic', 'description': 'Add a time delay', 'iconKey': 'Pause'},
            {'id': 'filter-array', 'name': 'Filter Array', 'type': 'logic', 'description': 'Filter array items', 'iconKey': 'Layers'},
            {'id': 'split', 'name': 'Split Paths', 'type': 'logic', 'description': 'Split workflow into parallel paths', 'iconKey': 'SplitSquareVertical'},
            {'id': 'join', 'name': 'Join Paths', 'type': 'logic', 'description': 'Join parallel paths', 'iconKey': 'Workflow'},
        ],
    },
    {
        'id': 'code',
        'name': 'Code',
        'iconKey': 'Code',
        'nodes': [
            {'id': 'javascript', 'name': 'JavaScript', 'type': 'code', 'description': 'Run JavaScript code', 'iconKey': 'Code'},
            {'id': 'python', 'name': 'Python', 'type': 'code', 'description': 'Run Python code', 'iconKey': 'Code'},
            {'id': 'c', 'name': 'C', 'type': 'code', 'description': 'Run C code', 'iconKey': 'Code'},
            {'id': 'bash', 'name': 'Bash', 'type': 'code', 'description': 'Run Bash scripts', 'iconKey': 'Terminal'},
            {'id': 'powershell', 'name': 'PowerShell', 'type': 'code', 'description': 'Run PowerShell scripts', 'iconKey': 'Terminal'},
            {'id': 'transform', 'name': 'Transform Data', 'type': 'code', 'description': 'Transform data structure', 'iconKey': 'FileJson'},
            {'id': 'json-path', 'name': 'JSON Path', 'type': 'code', 'description': 'Extract data using JSON Path', 'iconKey': 'FileJson'},
        ],
    },
    {
        'id': 'ai',
        'name': 'AI',
        'iconKey': 'Bot',
        'nodes': [
            {'id': 'ai-agent', 'name': 'AI Agent', 'type': 'ai', 'description': 'Use AI agents to process data', 'iconKey': 'Bot'},
            {'id': 'ai-transform', 'name': 'AI Transform', 'type': 'ai', 'description': 'Transform data using AI', 'iconKey': 'Sparkles'},
            {'id': 'input', 'name': 'Input', 'type': 'ai', 'description': 'Define input data for AI processing', 'iconKey': 'FileInput'},
            {'id': 'output-data', 'name': 'Output Data', 'type': 'ai', 'description': 'Format and output AI processed data', 'iconKey': 'FileOutput'},
            {'id': 'message', 'name': 'Send Message', 'type': 'message', 'description': 'Send a message response', 'iconKey': 'MessageSquare'},
            {'id': 'text-classification', 'name': 'Text Classification', 'type': 'ai', 'description': 'Classify text into categories', 'iconKey': 'Layers'},
            {'id': 'sentiment-analysis', 'name': 'Sentiment Analysis', 'type': 'ai', 'description': 'Analyze sentiment in text', 'iconKey': 'Gauge'},
            {'id': 'image-recognition', 'name': 'Image Recognition', 'type': 'ai', 'description': 'Identify objects in images', 'iconKey': 'ImageIcon'},
            {'id': 'data-extraction', 'name': 'Data Extraction', 'type': 'ai', 'description': 'Extract structured data from text', 'iconKey': 'FileJson'},
        ],
    },
    {
        'id': 'integrations',
        'name': 'Integrations',
        'iconKey': 'Share2',
        'nodes': [
            {'id': 'salesforce', 'name': 'Salesforce', 'type': 'integration', 'description': 'Interact with Salesforce CRM', 'iconKey': 'Building'},
            {'id': 'stripe', 'name': 'Stripe', 'type': 'integration', 'description': 'Process payments with Stripe', 'iconKey': 'CreditCard'},
            {'id': 'google-analytics', 'name': 'Google Analytics', 'type': 'integration', 'description': 'Track analytics data', 'iconKey': 'BarChart'},
            {'id': 'slack', 'name': 'Slack', 'type': 'integration', 'description': 'Send messages to Slack', 'iconKey': 'MessageSquare'},
            {'id': 'zendesk', 'name': 'Zendesk', 'type': 'integration', 'description': 'Manage support tickets', 'iconKey': 'Users'},
            {'id': 'hubspot', 'name': 'HubSpot', 'type': 'integration', 'description': 'Manage marketing and CRM', 'iconKey': 'Briefcase'},
        ],
    },
    {
        'id': 'banking',
        'name': 'Banking',
        'iconKey': 'Coins',
        'nodes': [
            {'id': 'transaction-processing', 'name': 'Transaction Processing', 'type': 'banking', 'description': 'Process financial transactions', 'iconKey': 'CreditCard'},
            {'id': 'account-verification', 'name': 'Account Verification', 'type': 'banking', 'description': 'Verify account details', 'iconKey': 'ShieldCheck'},
            {'id': 'fraud-detection', 'name': 'Fraud Detection', 'type': 'banking', 'description': 'Detect suspicious activities', 'iconKey': 'AlertCircle'},
            {'id': 'kyc', 'name': 'KYC Process', 'type': 'banking', 'description': 'Know Your Customer verification', 'iconKey': 'Fingerprint'},
            {'id': 'loan-approval', 'name': 'Loan Approval', 'type': 'banking', 'description': 'Automate loan approval process', 'iconKey': 'Scroll'},
        ],
    },
]
# -----------------------------------------------------------------------------------
#  Flatten nodes list
all_nodes = [node for category in node_categories for node in category['nodes']]


@register('click')
def click_handler(config, input_data, context):
    """
    Manual run trigger.
    """
    print("[click] Manual Run Triggered")
    return {'success': True, 'output': 'Manual run executed'}

# 5) Workflow executor

@register('chat')
def chat_handler(config, input_data, context):
    """
    Simulate processing an incoming chat message.
    Expects input_data = {'message': str}
    Returns a simple echo response.
    """
    msg = input_data.get('message', '')
    response = msg.upper()
    return {'success': True, 'output': response}



@register('schedule')
def schedule_handler(config, input_data, context):
    """
    Wait until a specified time, then return a timestamp.
    Config must include 'run_after_seconds': int
    """
    delay = config.get('run_after_seconds', 0)
    print(f"[schedule] Sleeping for {delay} seconds...")
    time.sleep(delay)
    now = datetime.now().isoformat()
    return {'success': True, 'output': f"Scheduled run at {now}"}

@register('webhook')
def webhook_handler(config, input_data, context):
    """
    Simulate receiving HTTP data via webhook.
    input_data = {'payload': dict}
    """
    payload = input_data.get('payload', {})
    # Business logic: acknowledge receipt
    return {'success': True, 'output': {'ack': True, 'received': payload}}

@register('http')
def http_handler(config, input_data=None, context=None):
    """
    Perform an HTTP request, or simulate it if SIMULATE is True.

    Args:
        config (dict):
            - url (str): the request URL (required)
            - method (str): HTTP method (default: GET)
            - headers (dict): optional headers
            - timeout (int|float): seconds before timing out (default: 30)
        input_data: 
            - dict/list for JSON body
            - str for raw/text body
        context: unused
    Returns:
        dict with 'success': bool, and either 'output' or 'error'
    """
    url = config.get('url')
    method = config.get('method', 'GET').upper()

    # Simulation branch
    if SIMULATE:
        return {
            'success': True,
            'output': {
                'url': url,
                'method': method,
                'status': 200,
                'simulated': True
            }
        }

    # ---- Real HTTP branch ----
    if not url:
        return {'success': False, 'error': 'Missing "url" in config.'}

    headers = config.get('headers', {})
    timeout = config.get('timeout', 30)

    # Decide how to send the body
    json_body = input_data if isinstance(input_data, (dict, list)) else None
    data_body = input_data if isinstance(input_data, str) else None

    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_body,
            data=data_body,
            timeout=timeout
        )
        resp.raise_for_status()

        # Try JSON, else text
        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        return {
            'success': True,
            'output': {
                'url': url,
                'method': method,
                'status': resp.status_code,
                'headers': dict(resp.headers),
                'body': body,
                'simulated': False
            }
        }

    except requests.RequestException as err:
        return {
            'success': False,
            'error': str(err),
            'output': {
                'url': url,
                'method': method,
                'simulated': False
            }
        }
    
@register('email-send')
def email_send_handler(config, input_data, context):
    """
    Simulate sending an email.
    Config: {'to': str, 'subject': str}
    input_data: {'body': str}
    """
    to = config.get('to')
    subj = config.get('subject')
    body = input_data.get('body', '')
    # Dummy send
    print(f"Sending email to {to}: {subj}")
    return {'success': True, 'output': f"Email sent to {to}"}


@register('ai-agent')
def ai_agent_handler(config, input_data, context):
    """
    Simulate AI agent processing.
    Config: {'model': str}
    input_data: {'data': str}
    """
    model = config.get('model')
    data = input_data.get('data', '')
    # Dummy processing
    print(f"Processing with AI model {model}: {data}")
    return {'success': True, 'output': f"Processed data with {model}"}


@register('if')
def if_handler(config, input_data, context):
    # config['condition'] should be a Python expression using 'context'
    cond_expr = config.get('condition', '')
    try:
        result = bool(eval(cond_expr, {}, {'context': context}))
        print(f"[if] Condition '{cond_expr}' evaluated to {result}")
        return {'success': True, 'output': result}
    except Exception as e:
        print(f"[if] Eval error: {e}")
        return {'success': False, 'output': False}
    
@register('message')
def message_handler(config, input_data, context):
    """
    Simulate sending a message.
    Config: {'recipient': str}
    input_data: {'message': str}
    """
    recipient = config.get('recipient')
    message = input_data.get('message', '')
    # Dummy send    
    print(f"Sending message to {recipient}: {message}")
    return {'success': True, 'output': f"Message sent to {recipient}"}


@register('output-data')
def output_data_handler(config, input_data, context):
    """
    Simulate formatting and outputting data.
    Config: {'format': str}
    input_data: {'data': dict}
    """
    format_type = config.get('format', 'json')
    data = input_data.get('data', {})
    # Dummy formatting
    if format_type == 'json':
        formatted_data = json.dumps(data)
    else:
        formatted_data = str(data)
    return {'success': True, 'output': formatted_data}

@register('python')
def python_code_handler(config, input_data, context):
    """
    Simulate executing Python code.
    Config: {'code': str}
    input_data: {'args': list}
    """
    code = config.get('code', '')
    args = input_data.get('args', [])
    # Dummy execution
    print(f"Executing Python code: {code} with args {args}")
    return {'success': True, 'output': f"Executed Python code with args {args}"}


@register('javascript')
def javascript_code_handler(config, input_data, context):
    """
    Simulate executing JavaScript code.
    Config: {'code': str}
    input_data: {'args': list}
    """
    code = config.get('code', '')
    args = input_data.get('args', [])
    # Dummy execution
    print(f"Executing JavaScript code: {code} with args {args}")
    return {'success': True, 'output': f"Executed JavaScript code with args {args}"}

@register('c')
def c_code_handler(config, input_data, context):
    """
    Simulate executing C code.
    Config: {'code': str}
    input_data: {'args': list}
    """
    code = config.get('code', '')
    args = input_data.get('args', [])
    # Dummy execution
    print(f"Executing C code: {code} with args {args}")
    return {'success': True, 'output': f"Executed C code with args {args}"}

@register('database')
def database_handler(config, input_data, context):
    """
    Simulate database operations.
    Config: {'query': str}
    input_data: {'params': dict}
    """
    query = config.get('query', '')
    params = input_data.get('params', {})
    # Dummy execution
    print(f"Executing database query: {query} with params {params}")
    return {'success': True, 'output': f"Executed database query with params {params}"}

@register('ai-rag')
def ai_rag_handler(config, input_data, context):
    """
    Simulate AI RAG (Retrieval-Augmented Generation) processing.
    Config: {'model': str}
    input_data: {'data': str}
    """
    model = config.get('model')
    data = input_data.get('data', '')
    # Dummy processing
    print(f"Processing with AI RAG model {model}: {data}")
    return {'success': True, 'output': f"Processed data with {model}"}

@register('ai-mcp')
def ai_mcp_handler(config, input_data, context):
    """
    Simulate AI MCP (Multi-Channel Processing) processing.
    Config: {'model': str}
    input_data: {'data': str}
    """
    model = config.get('model')
    data = input_data.get('data', '')
    # Dummy processing
    print(f"Processing with AI MCP model {model}: {data}")
    return {'success': True, 'output': f"Processed data with {model}"}

@register('ai-governance')
def ai_governance_handler(config, input_data, context):
    """
    Simulate AI Governance processing.
    Config: {'model': str}
    input_data: {'data': str}
    """
    model = config.get('model')
    data = input_data.get('data', '')
    # Dummy processing
    print(f"Processing with AI Governance model {model}: {data}")
    return {'success': True, 'output': f"Processed data with {model}"}

@register('googlesheets')
def googlesheets_handler(config, input_data, context):
    """
    Simulate Google Sheets operations.
    Config: {'action': str, 'sheet_id': str}
    input_data: {'data': list}
    """
    action = config.get('action', 'read')
    sheet_id = config.get('sheet_id', '')
    data = input_data.get('data', [])
    # Dummy execution
    print(f"Executing Google Sheets {action} on sheet {sheet_id} with data {data}")
    return {'success': True, 'output': f"Executed {action} on Google Sheets with data {data}"}

@register('ai-completion')
def ai_completion_handler(config, input_data, context):
    """
    Simulate AI text completion.
    Config: {'model': str}
    input_data: {'prompt': str}
    """
    model = config.get('model')
    prompt = input_data.get('prompt', '')
    # Dummy processing
    print(f"Generating text with AI model {model}: {prompt}")
    return {'success': True, 'output': f"Generated text with {model}"}


@register('form')
def form_handler(config, input_data, context):
    """
    Simulate form submission processing.
    Config: {'form_id': str}
    input_data: {'data': dict}
    """
    form_id = config.get('form_id', '')
    data = input_data.get('data', {})
    # Dummy processing
    print(f"Processing form submission for form {form_id}: {data}")
    return {'success': True, 'output': f"Processed form submission for {form_id}"}

@register('ai')
def ai_handler(config, input_data, context):
    """
    Simulate AI processing.
    Config: {'model': str}
    input_data: {'data': str}
    """
    model = config.get('model')
    data = input_data.get('data', '')
    # Dummy processing
    print(f"Processing with AI model {model}: {data}")
    return {'success': True, 'output': f"Processed data with {model}"}

@register('email')
def email_handler(config, input_data, context):
    """
    Simulate email processing.
    Config: {'action': str}
    input_data: {'data': dict}
    """
    action = config.get('action', 'send')
    data = input_data.get('data', {})
    # Dummy execution
    print(f"Executing email {action} with data {data}")
    return {'success': True, 'output': f"Executed email {action} with data {data}"}

@register('document')
def document_handler(config, input_data, context):
    """
    Simulate document processing.
    Config: {'action': str}
    input_data: {'data': dict}
    """
    action = config.get('action', 'read')
    data = input_data.get('data', {})
    # Dummy execution
    print(f"Executing document {action} with data {data}")
    return {'success': True, 'output': f"Executed document {action} with data {data}"}

@register('calendar')
def calendar_handler(config, input_data, context):
    """
    Simulate calendar operations.
    Config: {'action': str}
    input_data: {'data': dict}
    """
    action = config.get('action', 'create')
    data = input_data.get('data', {})
    # Dummy execution
    print(f"Executing calendar {action} with data {data}")
    return {'success': True, 'output': f"Executed calendar {action} with data {data}"}

