"""
Этот файл создан для обхода проблемы с asyncio на Windows в Python 3.13
"""
import uvicorn
import sys
import os
import signal

if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = "1"
    os.environ["PYTHONDEVMODE"] = "1"
    
    if sys.platform == 'win32':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8001, 
        log_level="info",
        workers=1,
        reload=False
    )
