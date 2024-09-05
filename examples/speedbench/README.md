Results here show at a glance that raising an error will always be faster than handling it:

```
Service Type                        Valid Input     Invalid Input
-----------------------------------------------------------------
baseline_service                    1.00            1.01
validate_call_service               1.36            1.33
validate_call_safe_service          1.57            40.23
validate_call_return_service        1.60            1.27
validate_call_safe_return_service   1.85            39.70
```

However the relative slowdown of 15% here is fairly minimal.
Not to mention that in a real program much more would be done than just ingesting input and emitting output!
