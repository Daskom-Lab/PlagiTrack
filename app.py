from aiohttp import web
from concurrent.futures import ProcessPoolExecutor
import asyncio
import aiohttp_jinja2
import jinja2
import os
import shutil
from glob import glob
from core import allowed_file, compare, process_ai_detection, process_similarity, UPLOAD_FOLDER, STATIC_FOLDER, LEAST_PLG, TF_FACTOR

# Route Handlers
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}

@aiohttp_jinja2.template('dashboard.html')
async def dashboard(request):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    files = [file.removeprefix(UPLOAD_FOLDER + '/') for file in glob(UPLOAD_FOLDER + '/*.c')]
    return {"files": files}

async def upload_files(request):
    reader = await request.multipart()
    async for field in reader:
        filename = field.filename
        if filename and allowed_file(filename):
            # Sanitize
            filename = os.path.basename(filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
    return web.HTTPFound(location='/dashboard')

async def delete_files(request):
    shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)
    return web.HTTPFound(location='/dashboard')

async def similarity(request):
    
    return web.HTTPFound(location='/dashboard')

@aiohttp_jinja2.template('result.html')
async def result(request):
    return {}

@aiohttp_jinja2.template('uncommon.html')
async def check_ai(request):
    return {}

@aiohttp_jinja2.template('similarity.html')
async def similarity(request):
    return {}

async def handle_similarity(request):
    data = await request.json()
    programs = glob(UPLOAD_FOLDER+'/*.c')
    transformation_factor = data.get("transformation_factor", TF_FACTOR)
    least_plagiarism = data.get("least_plagiarism", LEAST_PLG)

    # Run CPU-intensive task in ProcessPoolExecutor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, process_similarity, programs, transformation_factor, least_plagiarism
    )
    return web.json_response(result)

async def handle_compare(request):
    """
    Handles the POST request to compare two programs.
    """
    try:
        data = await request.json()
        program1 = data.get("program1")
        program2 = data.get("program2")

        # Validate input
        if not program1 or not program2:
            return web.json_response({"error": "Both program1 and program2 are required"}, status=400)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, compare, program1, program2)

        # Return the PDF as a response
        return web.json_response({"message": "Comparison completed successfully"}, status=200)

    except Exception as e:
        print(e)
        return web.json_response({"error": f"An error occurred: {str(e)}"}, status=500)


# Setup Routes Function
def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/dashboard', dashboard)
    app.router.add_post('/upload', upload_files)
    app.router.add_post('/delete', delete_files)
    app.router.add_post("/compare", handle_compare)
    app.router.add_get('/process-ai-detection', process_ai_detection)
    app.router.add_post('/process-similarity', handle_similarity)
    app.router.add_get('/dashboard/similarity', similarity)
    app.router.add_get('/dashboard/check-ai', check_ai)
    app.router.add_post('/dashboard/result', result)
    app.router.add_get('/dashboard/result', result)
    app.router.add_static('/static/', STATIC_FOLDER)


# App Setup
app = web.Application()
executor = ProcessPoolExecutor(max_workers=8)

# Configure Jinja2 Template Engine
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))

setup_routes(app)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True) 
    web.run_app(app, host='127.0.0.1', port=8080)
