```python
"""
Detect available hardware and choose best execution path.
"""

def detect_capabilities():
    """
    Probe system for:
    - OpenCL devices
    - Available RAM
    - CPU cores
    - Thermal limits
    """
    capabilities = {
        'opencl': False,
        'devices': [],
        'ram_mb': 0,
        'cores': 1,
        'thermal_warning': False
    }
    
    # Check OpenCL
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        if platforms:
            capabilities['opencl'] = True
            for platform in platforms:
                devices = platform.get_devices()
                for device in devices:
                    capabilities['devices'].append({
                        'name': device.name,
                        'type': str(device.type),
                        'memory': device.global_mem_size // (1024*1024)
                    })
    except:
        pass
        
    # Check CPU cores
    import multiprocessing
    capabilities['cores'] = multiprocessing.cpu_count()
    
    # Check RAM (Linux/Mac/Windows fallback)
    try:
        import psutil
        capabilities['ram_mb'] = psutil.virtual_memory().total // (1024*1024)
    except:
        # Simple fallback
        capabilities['ram_mb'] = 1024  # Assume 1GB
        
    # Thermal check (rough)
    if capabilities.get('ram_mb', 0) < 512:
        capabilities['thermal_warning'] = True
        
    return capabilities


def choose_strategy(capabilities):
    """
    Choose best execution strategy based on available hardware.
    """
    if capabilities['opencl'] and capabilities['ram_mb'] > 256:
        return 'gpu'
    elif capabilities['cores'] > 1:
        return 'multicore'
    else:
        return 'single'
```
