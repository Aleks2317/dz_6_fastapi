import uvicorn
from fastapi import FastAPI
from fastapi.params import Path
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()
tasks = []


class Tasks(BaseModel):
    id: int = Field(title='первичный ключ')
    title: str = Field(title='название задачи', max_length=50)
    description: str = Field(title='описание задачи', max_length=200)
    status: bool = Field(title='статус выполнения задачи', default=False)


@app.get('/tasks/', response_model=List[Tasks])
async def get_tasks():
    return tasks


@app.get('/tasks/{task_id}', response_model=Tasks)
async def get_task(task_id: int = Path(..., ge=0, le=len(tasks))):
    return tasks[task_id]


@app.post('/tasks/', response_model=Tasks)
async def create_task(task: Tasks):
    tasks.append(task)
    return task


@app.put('/tasks/{task_id}', response_model=Tasks)
async def update_task(new_task: Tasks, task_id: int = Path(..., ge=0, le=len(tasks))):
    tasks[task_id] = new_task
    return new_task


@app.delete('/tasks/{task_id}', response_model=Tasks)
async def delete_task(task_id: int = Path(..., ge=0, le=len(tasks))):
    return tasks.pop(task_id)


if __name__ == '__main__':
    uvicorn.run("main_03:app", host="127.0.0.1", port=8000, reload=True)
