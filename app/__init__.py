import time
import redis
import json
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Request, BackgroundTasks
from sqlalchemy.orm import Session

from .model import AsteroidSchema
from .database import SessionLocal, engine, Base
from .config import settings
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port, db=0,
    password=settings.redis_password)


def log_to_redis(key, body):
    logs = []
    if redis_client.exists(key):
        logs = json.loads(redis_client.get(key))
        logs.append(body)
        redis_client.set(key, json.dumps(logs))
    else:
        redis_client.set(key, json.dumps([body]))
        logs = [body]
    return logs


def generate_report(data):
    lis = log_to_redis('create', data)
    if len(lis) == 20:
        out_file = open(f"create_report_at_{int(time.time())}", "w")
        json.dump(lis, out_file)
        redis_client.set('create', json.dumps([]))


@app.middleware("http")
async def add_process_time_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 5)
    log = {'at': int(time.time()), 'time': process_time, **request.path_params,
           'method': request.method, 'client': request.client.host, 'path': request.url.path}
    log_to_redis('logs', log)
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def alert_bruce_wills(data):
    if settings.production in ['true', True]:
        # implement communication to bruce wills here
        pass
    else:
        pass


router = APIRouter()


@router.get("/asteroids")
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = AsteroidSchema.get_all(db, skip=skip, limit=limit)
    return data


@router.get("/asteroids/{id}", response_model=AsteroidSchema)
def read_one(id: int, db: Session = Depends(get_db)):
    asteroid = AsteroidSchema.get_one(db, id)
    if asteroid is None:
        return {'data': asteroid, 'success': True}
    else:
        raise HTTPException(status_code=404, detail="Asteroid not found")


@router.post("/asteroids", response_model=AsteroidSchema)
def create_one(astro: AsteroidSchema,
               tasks: BackgroundTasks,
               db: Session = Depends(get_db)):
    yes = astro.save(db)
    if yes:
        col = astro.collision
        size = astro.size
        if (col > 0.7 or size > 1000) or (col > 0.9 and size > 100):
            tasks.add_task(alert_bruce_wills, astro.dict())
        tasks.add_task(generate_report, astro.dict())
        return {'success': True, **yes}
    else:
        raise HTTPException(
            status_code=403, detail="failed to create Asteroid")


@router.put("/asteroids/{id}", response_model=AsteroidSchema)
def update_one(id: str, astro: AsteroidSchema,
               tasks: BackgroundTasks,
               db: Session = Depends(get_db)):
    yes = astro.save(db, id=id)
    if yes:
        col = astro.collision
        size = astro.size
        if (col > 0.7 or size > 1000) or (col > 0.9 and size > 100):
            tasks.add_task(alert_bruce_wills, astro.dict())
        return {'success': True, **yes}
    else:
        raise HTTPException(
            status_code=403, detail="failed to update Asteroid")


@router.delete("/asteroids/{id}")
def delete_one(id: int, db: Session = Depends(get_db)):
    yes = AsteroidSchema.delete_one(db, id)
    if yes:
        return {**yes}
    else:
        raise HTTPException(status_code=404, detail="Asteroid not found")


app.include_router(router, tags=['Asteroids'])
