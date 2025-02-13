from fastapi import FastAPI
from route import router
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
handler=Mangum(app)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173',
                   'https://vericaptcha.live',
                   'https://www.vericaptcha.live'
                   ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)