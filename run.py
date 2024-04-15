import uvicorn

from src import create_app
from src.db.mongo_db import connect_to_mongodb

app = create_app()

app.add_event_handler("startup", connect_to_mongodb)


if __name__ == '__main__':
    uvicorn.run('run:app', host='0.0.0.0', port=8000, reload=True)
