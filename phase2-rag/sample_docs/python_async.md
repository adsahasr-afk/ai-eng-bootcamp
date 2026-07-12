# Async Python Notes

Async programming in Python uses the async and await keywords. An async function
is called a coroutine.

The event loop schedules and runs coroutines. asyncio.run() starts the event
loop and runs a coroutine to completion.

await suspends a coroutine until an awaitable completes, which lets other tasks
run in the meantime.

asyncio.gather() runs multiple coroutines concurrently and collects their
results into a list.

Async is best for I/O-bound workloads such as network calls, not CPU-bound work.
FastAPI supports async endpoints for handling many requests concurrently.
