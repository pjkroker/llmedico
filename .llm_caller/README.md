(3) Enable Port Forwarding:

```bash
ssh -f -N -L 0.0.0.0:11434:localhost:11434 -o ServerAliveInterval=60 -o ServerAliveCountMax=5 gruenau1.informatik.hu-berlin.de
```