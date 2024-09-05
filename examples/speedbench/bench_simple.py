import timeit
from pydantic import BaseModel, validate_call, ValidationError
from validate_call_safe import validate_call_safe


# Baseline model
class Event(BaseModel):
    id: int
    name: str


# Service implementations
def baseline_service(event_data: dict):
    try:
        event = Event(**event_data)
        return {"processed": True, "event_id": event.id}
    except ValidationError:
        return {"processed": False, "error": "Invalid input"}


@validate_call
def validate_call_service(event: Event) -> dict:
    return {"processed": True, "event_id": event.id}


@validate_call_safe
def validate_call_safe_service(event: Event) -> dict:
    return {"processed": True, "event_id": event.id}


@validate_call(validate_return=True)
def validate_call_return_service(event: Event) -> dict:
    return {"processed": True, "event_id": event.id}


@validate_call_safe(validate_return=True)
def validate_call_safe_return_service(event: Event) -> dict:
    return {"processed": True, "event_id": event.id}


# Test data
valid_event = {"id": 1, "name": "Test Event"}
invalid_event = {"id": "not an int", "name": "Invalid Event"}


# Benchmark function
def benchmark(func, input_data, num_iterations=10000):
    def wrapper():
        try:
            func(input_data)
        except ValidationError:
            pass  # Ignore ValidationError for validate_call services

    return timeit.timeit(wrapper, number=num_iterations)


# Run benchmarks
def run_benchmarks():
    print("Running benchmarks...")
    print(f"{'Service Type':<35} {'Valid Input':<15} {'Invalid Input':<15}")
    print("-" * 65)

    services = [
        baseline_service,
        validate_call_service,
        validate_call_safe_service,
        validate_call_return_service,
        validate_call_safe_return_service,
    ]

    baseline_valid = benchmark(baseline_service, valid_event)
    baseline_invalid = benchmark(baseline_service, invalid_event)

    for service in services:
        valid_time = benchmark(service, valid_event)
        invalid_time = benchmark(service, invalid_event)

        valid_relative = valid_time / baseline_valid
        invalid_relative = invalid_time / baseline_invalid

        print(
            f"{service.__name__:<35} {valid_relative:<15.2f} {invalid_relative:<15.2f}",
        )


if __name__ == "__main__":
    run_benchmarks()
